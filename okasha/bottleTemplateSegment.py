"""
this is a segment from bottle
Homepage and documentation: http://bottle.paws.de/

Licence (MIT)
-------------

    Copyright (c) 2009, Marcel Hellkamp.

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.
"""

import sys, os, os.path, tokenize, functools, re
from cgi import escape
from baseWebApp import webAppBaseException

#########################

class TemplateError(webAppBaseException):
    def __init__(self, message):
        webAppBaseException.__init__(self, 500, message)

#########################
# taken from bottle at 5-Jul-2010
# http://github.com/defnull/bottle/tree/81bf74c36c4652958914d26ea91ec345e381572c
#########################

if sys.version_info >= (3,0,0): # pragma: no cover
    # See Request.POST
    from io import BytesIO
    from io import TextIOWrapper
    class NCTextIOWrapper(TextIOWrapper):
        ''' Garbage collecting an io.TextIOWrapper(buffer) instance closes the
            wrapped buffer. This subclass keeps it open. '''
        def close(self): pass
    StringType = bytes
    def touni(x, enc='utf8'): # Convert anything to unicode (py3)
        return str(x, encoding=enc) if isinstance(x, bytes) else str(x)
else:
    from StringIO import StringIO as BytesIO
    from types import StringType
    NCTextIOWrapper = None
    def touni(x, enc='utf8'): # Convert anything to unicode (py2)
        return x if isinstance(x, unicode) else unicode(str(x), encoding=enc)

def tob(data, enc='utf8'): # Convert strings to bytes (py2 and py3)
    return data.encode(enc) if isinstance(data, unicode) else data


class BaseTemplate(object):
    """ Base class and minimal API for template adapters """
    extentions = ['tpl','html','thtml','stpl']
    settings = {} #used in prepare()
    defaults = {} #used in render()

    def __init__(self, source=None, name=None, lookup=[], encoding='utf8', **settings):
        """ Create a new template.
        If the source parameter (str or buffer) is missing, the name argument
        is used to guess a template filename. Subclasses can assume that
        self.source and/or self.filename are set. Both are strings.
        The lookup, encoding and settings parameters are stored as instance
        variables.
        The lookup parameter stores a list containing directory paths.
        The encoding parameter should be used to decode byte strings or files.
        The settings parameter contains a dict for engine-specific settings.
        """
        self.name = name
        self.source = source.read() if hasattr(source, 'read') else source
        self.filename = source.filename if hasattr(source, 'filename') else None
        self.lookup = map(os.path.abspath, lookup)
        self.encoding = encoding
        self.settings = self.settings.copy() # Copy from class variable
        self.settings.update(settings) # Apply 
        if not self.source and self.name:
            self.filename = self.search(self.name, self.lookup)
            if not self.filename:
                raise TemplateError('Template %s not found.' % repr(name))
        if not self.source and not self.filename:
            raise TemplateError('No template specified.')
        self.prepare(**self.settings)

    @classmethod
    def search(cls, name, lookup=[]):
        """ Search name in all directiries specified in lookup.
        First without, then with common extentions. Return first hit. """
        if os.path.isfile(name): return name
        for spath in lookup:
            fname = os.path.join(spath, name)
            if os.path.isfile(fname):
                return fname
            for ext in cls.extentions:
                if os.path.isfile('%s.%s' % (fname, ext)):
                    return '%s.%s' % (fname, ext)

    @classmethod
    def global_config(cls, key, *args):
        ''' This reads or sets the global settings stored in class.settings. '''
        if args:
            cls.settings[key] = args[0]
        else:
            return cls.settings[key]

    def prepare(self, **options):
        """ Run preparatios (parsing, caching, ...).
        It should be possible to call this again to refresh a template or to
        update settings.
        """
        raise NotImplementedError

    def render(self, **args):
        """ Render the template with the specified local variables and return
        a single byte or unicode string. If it is a byte string, the encoding
        must match self.encoding. This method must be thread save!
        """
        raise NotImplementedError


class SimpleTemplate(BaseTemplate):
    blocks = ('if','elif','else','try','except','finally','for','while','with','def','class')
    dedent_blocks = ('elif', 'else', 'except', 'finally')

    def prepare(self, escape_func=escape, noescape=False):
        self.cache = {}
        if self.source:
            self.code = self.translate(self.source)
            self.co = compile(self.code, '<string>', 'exec')
        else:
            self.code = self.translate(open(self.filename).read())
            self.co = compile(self.code, self.filename, 'exec')
        enc = self.encoding
        self._str = lambda x: touni(x, enc)
        self._escape = lambda x: escape_func(touni(x, enc))
        if noescape:
            self._str, self._escape = self._escape, self._str

    def translate(self, template):
        stack = [] # Current Code indentation
        lineno = 0 # Current line of code
        ptrbuffer = [] # Buffer for printable strings and token tuple instances
        codebuffer = [] # Buffer for generated python code
        touni = functools.partial(unicode, encoding=self.encoding)
        multiline = dedent = False

        def yield_tokens(line):
            for i, part in enumerate(re.split(r'\{\{(.*?)\}\}', line)):
                if i % 2:
                    if part.startswith('!'): yield 'RAW', part[1:]
                    else: yield 'CMD', part
                else: yield 'TXT', part

        def split_comment(codeline):
            """ Removes comments from a line of code. """
            line = codeline.splitlines()[0]
            try:
                tokens = list(tokenize.generate_tokens(iter(line).next))
            except tokenize.TokenError:
                return line.rsplit('#',1) if '#' in line else (line, '')
            for token in tokens:
                if token[0] == tokenize.COMMENT:
                    start, end = token[2][1], token[3][1]
                    return codeline[:start] + codeline[end:], codeline[start:end]
            return line, ''

        def flush(): # Flush the ptrbuffer
            if not ptrbuffer: return
            cline = ''
            for line in ptrbuffer:
                for token, value in line:
                    if token == 'TXT': cline += repr(value)
                    elif token == 'RAW': cline += '_str(%s)' % value
                    elif token == 'CMD': cline += '_escape(%s)' % value
                    cline +=  ', '
                cline = cline[:-2] + '\\\n'
            cline = cline[:-2]
            if cline[:-1].endswith('\\\\\\\\\\n'):
                cline = cline[:-7] + cline[-1] # 'nobr\\\\\n' --> 'nobr'
            cline = '_printlist([' + cline + '])'
            del ptrbuffer[:] # Do this before calling code() again
            code(cline)

        def code(stmt):
            for line in stmt.splitlines():
                codebuffer.append('  ' * len(stack) + line.strip())

        for line in template.splitlines(True):
            lineno += 1
            line = line if isinstance(line, unicode)\
                        else unicode(line, encoding=self.encoding)
            if lineno <= 2:
                m = re.search(r"%.*coding[:=]\s*([-\w\.]+)", line)
                if m: self.encoding = m.group(1)
                if m: line = line.replace('coding','coding (removed)')
            if line.strip()[:2].count('%') == 1:
                line = line.split('%',1)[1].lstrip() # Full line following the %
                cline = split_comment(line)[0].strip()
                cmd = re.split(r'[^a-zA-Z0-9_]', cline)[0]
                flush() ##encodig (TODO: why?)
                if cmd in self.blocks or multiline:
                    cmd = multiline or cmd
                    dedent = cmd in self.dedent_blocks # "else:"
                    if dedent and not oneline and not multiline:
                        cmd = stack.pop()
                    code(line)
                    oneline = not cline.endswith(':') # "if 1: pass"
                    multiline = cmd if cline.endswith('\\') else False
                    if not oneline and not multiline:
                        stack.append(cmd)
                elif cmd == 'end' and stack:
                    code('#end(%s) %s' % (stack.pop(), line.strip()[3:]))
                elif cmd == 'include':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code("_=_include(%s, _stdout, %s)" % (repr(p[0]), p[1]))
                    elif p:
                        code("_=_include(%s, _stdout)" % repr(p[0]))
                    else: # Empty %include -> reverse of %rebase
                        code("_printlist(_base)")
                elif cmd == 'rebase':
                    p = cline.split(None, 2)[1:]
                    if len(p) == 2:
                        code("globals()['_rebase']=(%s, dict(%s))" % (repr(p[0]), p[1]))
                    elif p:
                        code("globals()['_rebase']=(%s, {})" % repr(p[0]))
                else:
                    code(line)
            else: # Line starting with text (not '%') or '%%' (escaped)
                if line.strip().startswith('%%'):
                    line = line.replace('%%', '%', 1)
                ptrbuffer.append(yield_tokens(line))
        flush()
        return '\n'.join(codebuffer) + '\n'

    def subtemplate(self, _name, _stdout, **args):
        # NOTE: the following 2 lines added for okasha
        if not args.has_key('_r'):
          if self._r: args['_r']=self._r
        if _name not in self.cache:
            self.cache[_name] = self.__class__(name=_name, lookup=self.lookup)
        return self.cache[_name].execute(_stdout, **args)

    def execute(self, _stdout, **args):
        # NOTE: the following 5 lines added for okasha
        if not hasattr(self, '_r'): self._r=None
        if args.has_key('_r'):
          if not self._r: self._r=args['_r']
        else:
          if self._r: args['_r']=self._r

        env = self.defaults.copy()
        env.update({'_stdout': _stdout, '_printlist': _stdout.extend,
               '_include': self.subtemplate, '_str': self._str,
               '_escape': self._escape})
        env.update(args)
        eval(self.co, env)
        if '_rebase' in env:
            subtpl, rargs = env['_rebase']
            subtpl = self.__class__(name=subtpl, lookup=self.lookup)
            subtpl._r=self._r # NOTE: this line is added for okasha
            rargs['_base'] = _stdout[:] #copy stdout
            del _stdout[:] # clear stdout
            return subtpl.execute(_stdout, **rargs)
        return env

    def render(self, **args):
        """ Render the template using keyword arguments as local variables. """
        stdout = []
        self.execute(stdout, **args)
        return ''.join(stdout)

