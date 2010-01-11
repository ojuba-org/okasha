# -*- coding: utf-8 -*-
"""
Okasha - a very simple WSGI webframe work
Copyright © 2009, Muayyad Alsadi <alsadi@ojuba.org>

    Released under terms of Waqf Public License.
    This program is free software; you can redistribute it and/or modify
    it under the terms of the latest version Waqf Public License as
    published by Ojuba.org.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

    The Latest version of the license can be found on
    "http://waqf.ojuba.org/license"

"""

import sys, os, os.path
import json # for templates
import urlparse # for parsing query string
from cgi import escape # for html escaping
from Cookie import SimpleCookie # in python 3.0 it's from http.cookies import SimpleCookie

#import urllib # to be used for quote and unquote

# TODO: use c=Cookie.SimpleCookie(string)

webAppResponses={
    200:'200 OK',
    302:'302 Temporary Redirect',
    403:'403 Forbidden',
    404:'404 Not Found',
    500:'500 Internal Server Error'
  }

class webAppBaseException(Exception):
  """
  exceptions like fileNotFoundException
  """
  def __init__(self, code, *args,**kw):
    self.code=code
    self.args=args
    self.kw=kw
    

forbiddenException=lambda *a,**kw: webAppBaseException(403,*a,**kw)
fileNotFoundException=lambda *a,**kw: webAppBaseException(404,*a,**kw)
def redirectException(location,*a,**kw):
  e=webAppBaseException(302,*a,**kw)
  if type(location)==unicode: l=location.encode('utf-8')
  else: l=location
  e.kw['location']=l
  return e


class Response:
  def __init__(self, code=None,contentType=None,headers=None):
    self.code=code
    self.contentType=contentType
    self.headers=headers

class Request:
  def __init__(self, webapp, environ, start_response):
    self.webapp=webapp
    self.script=environ.get('SCRIPT_NAME','') # the uri of the webapp
    self.environ=environ
    self.start_response=start_response
    self.response=Response()
    # FIXME: find a way to simplify decoding query strings into unicode
    qs=environ.get('QUERY_STRING','')
    self.q=urlparse.parse_qs(qs)

    try: self.cookies=SimpleCookie(environ.get('HTTP_COOKIE','')) # cookies['key'].value
    except: self.cookies=SimpleCookie('')

    self.uri=environ['PATH_INFO'] # can be / or /view 
    
    if type(self.uri)!=unicode:
      try: self.uri=self.uri.decode('utf8')
      except UnicodeDecodeError: self.uri=None

    if self.uri.endswith('/'): self.tailingSlash=True
    else: self.tailingSlash=False
    if self.uri.startswith('/'): self.uriList=self.uri[1:].split('/')
    else: self.uriList=self.uri.split('/') # NOTE: this should never happen
    if self.uriList and self.uriList[-1]=='': self.uriList.pop()
    

class expose:
  def __init__(self, template=None, templateArgs=[],templateKw={},
    responseCode=200, contentType='text/html; charset=utf-8', headers={},
    requiresTailingSlash=False
    ):
    """
    a decorator that applies the result of the function to the provided template
    """
    self._template=template
    self._templateArgs=templateArgs
    self._templateKw=templateKw
    self._response=responseCode
    self._contentType=contentType
    self._headers=headers
    self._requiresTailingSlash=requiresTailingSlash
    
  def __call__(self, func):
    def wrapper(*args):
      if not args: raise webAppBaseException(500)
      elif isinstance(args[0],baseWebApp) and len(args)>=2:
        rq=args[1]
      else:
        rq=args[0]
      if self._requiresTailingSlash and not rq.tailingSlash:
        raise redirectException(rq.script+rq.uri+'/')
      # FIXME: do we need here a try: except:
      if self._template:
        r=self._template(rq, func(*args), *self._templateArgs, **self._templateKw)
      else: r=func(*args)

      # fix response
      if rq.response.code==None: rq.response.code=self._response
      if rq.response.contentType==None: rq.response.contentType=self._contentType
      # FIXME: it should be merged not replaced
      if rq.response.headers==None: rq.response.headers=self._headers
      
      rs=webAppResponses.get(rq.response.code,"%d Unknown code" % rq.response.code)
      rq.start_response(rs, [('content-type', rq.response.contentType)]+map(lambda k: (k,rq.response.headers[k]),rq.response.headers))
      if type(r)==unicode: return (r.encode('utf8'),)
      elif isinstance(r, basestring): return (r,)
      return r
    return wrapper

def percentTemplate(rq, v, bfn=None):
  # FIXME: don't print error, just raise things and allow the controller to catch that to handle it and use its own logger
  d=rq.webapp._templatesDir
  if not os.path.isdir(d): raise fileNotFoundException()
  if not bfn: bfn='root.html'
  fn=os.path.join(d, bfn)
  try: tmp=open(fn,'rt').read().decode('utf-8')
  except IOError: raise fileNotFoundException()
  except:
    rq.webapp._logger.debug('template error fn=[%s]' % fn)
    raise
  # Note: try is used to check for valid template
  #try: s=[(tmp % v).encode('utf-8')] # NOTE: it expects a byte sequence not unicode object
  try: s=tmp % v # NOTE: it expects a byte sequence not unicode object
  except TypeError: raise KeyError
  except KeyError: raise TypeError
  return s

def jsonDumps(rq, o):
  if not rq.response.contentType:
    rq.response.contentType='application/x-javascript; charset=utf-8'
  return json.dumps(o, ensure_ascii=False)

class fakeLogger:
  def debug(msg): pass
  def info(msg): pass
  def warning(msg): pass
  def error(msg): pass
  def critical(msg): pass

class baseWebApp:
  """
  The base for our web Application, it's a mini web framework
  """
  _mimeByExtension={
    'html': 'text/html', 'txt': 'text/plain', 'css': 'text/css',
    'js':'application/javascript',
    'png': 'image/png', 'gif': 'image/gif', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'
  }

  def __init__(self, templatesDir, staticBaseDir={}, redirectBaseUrls={}, logger=fakeLogger(), debug=False):
    """
    staticBaseDirs: a dictionary of prefixes and corresponding directories for serving static content
    redirectBaseUrls: just like staticBaseDirs, but redirect to this BaseUrls instead of surving them
    
    if a prefix is specified in both, redirectBaseUrls will be used.
    
    logger is logging object from python logging module
    """
    self._logger=logger
    # TODO: add a self._templateFilesCache
    self._templatesDir=templatesDir
    # TODO: add a self._staticFilesCache
    self._staticBaseDir={}
    self._debug=debug # FIXME: no longer needed
    for k in staticBaseDir:
      v=staticBaseDir[k]
      if not os.path.isdir(v):
        self._logger.warning("WARNING: directory [%s] not found, skipping" % v)
        continue
      self._staticBaseDir[self._tailingSlash(k)]=self._tailingSlash(os.path.abspath(v))

    self._redirectBaseUrls={}
    for k in redirectBaseUrls:
      self._redirectBaseUrls[self._tailingSlash(k)]=self._tailingSlash(redirectBaseUrls[k])
    self._staticBaseDirKeys=self._staticBaseDir.keys()
    self._staticBaseDirKeys.sort()
    self._staticBaseDirKeys.reverse() # so it's from longer to shorter
    self._redirectBaseUrlsKeys=self._redirectBaseUrls.keys()
    self._redirectBaseUrlsKeys.sort()
    self._redirectBaseUrlsKeys.reverse()

  def _tailingSlash(self, s):
    if not s.endswith('/'): return s+'/'
    return s

  def _handleException(self, rq, e):
    s='_'+str(e.code)
    if hasattr(self, s):
      return getattr(self, s)(rq, e)
    return self._genericException(rq, e)

  def _genericException(self, rq, e):
    rs=webAppResponses.get(e.code,"%d Unknown code" % e.code)
    if rq.uri: s="exception [%s] happened when visiting [%s]" % (rs,rq.uri)
    else: s="exception [%s] happened" % rs
    rq.start_response(rs, [('content-type', 'text/plain')])
    return [s]

  def _302(self, rq, e):
    rs=webAppResponses[302]
    rq.start_response(rs, [
      ('content-type', 'text/plain'),('Location', e.kw['location'])
      ])
    return ("Redirect to "+ e.kw['location'],)

# you may customize exceptions like this
#  @expose(response=404,contentType='text/plain; charset=utf-8')
#  def _404(self, rq, e):
#    if not rq.uri: return ('File was not found',)
#    return ('File [%s] was not found' % rq.uri,)

  def __serveStatic(self, rq, fn):
    """
    internal method to serve static files like png, css,js  ...etc.
    """
    if not os.path.exists(fn): raise fileNotFoundException()
    try: f=open(fn,'rb')
    except IOError: raise fileNotFoundException()

    ext=fn[fn.rfind('.'):][1:].lower()
    rq.start_response("200 OK", [('content-type', self._mimeByExtension.get(ext,"application/octet-stream"))])
    # NOTE: since the file object is iteratable then no need for returning [r.read()]
    return f

  def __call__(self, environ, start_response):
    rq=Request(self, environ, start_response)
    if rq.uri==None:
      # handle malformed uri
      return self._handleException(rq, webAppBaseException(500))
    self._logger.info('got uri=[%s]' % rq.uri)
    self._logger.debug('got env=[%s]' % rq.environ)
    # check if we need to serve static content
    for k in self._staticBaseDirKeys:
      if rq.uri.startswith(k):
        # SECURITY CHECK: that filename is really in side base filename ie. no ".." trick
        # NOTE: no need for this check as it seems to be done by paste
        bfn=self._staticBaseDir[k]
        fn=bfn+rq.uri[len(k):]
        if not os.path.abspath(fn).startswith(bfn):
          return self._handleException(rq, forbiddenException())
        try: return self.__serveStatic(rq, fn)
        except webAppBaseException as e:
          return self._handleException(rq, e)
    # check if we need to serve redirect
    for k in self._redirectBaseUrlsKeys:
      if rq.uri.startswith(k):
        u=self._redirectBaseUrls[k]+rq.uri[len(k):]
        # FIXME: should we escape Location in start_response
        start_response("302 Temporary Redirect", [('Location',u),('content-type', 'text/html')])
        return [('<html><body><a href="%s">moved</a></body></html>' % escape(u))]
    # pass control to the right method
    if rq.uriList and not rq.uriList[0].startswith('_') and hasattr(self, rq.uriList[0]):
      f=getattr(self, rq.uriList[0])
      a=rq.uriList[1:]
    else:
      f=self._root
      a=rq.uriList
    try: r=f(rq, *a)
    except webAppBaseException as e:
      return self._handleException(rq, e)
    return r

  @expose()
  def _root(self, rq, *args):
    """
    called when no suitable method is found and it will be called for / too
    """
    return '''<html><body>You requested [<strong>%s</strong>]</body></html>'''% '/'.join(args)

if __name__ == '__main__':
    # this requires python-paste package
    from paste import httpserver
    app=baseWebApp(
      '/path/to/templates/files/',
      staticBaseDir={'/_files/':'/path/to/static/files/'}
    );
    # for options see http://pythonpaste.org/modules/httpserver.html
    httpserver.serve(app, host='127.0.0.1', port='8080')

