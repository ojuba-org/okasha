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
  def __init__(self, stat,uri=None, **kw):
    self.stat=stat
    self.uri=uri
    self.kw=kw

forbiddenException=lambda *a,**kw: webAppBaseException(403,*a,**kw)
fileNotFoundException=lambda *a,**kw: webAppBaseException(404,*a,**kw)
def redirectException(location,*a,**kw):
  e=webAppBaseException(302,*a,**kw)
  if type(location)==unicode: l=location.encode('utf-8')
  else: l=location
  e.kw['location']=l
  return e

class expose:
  def __init__(self, template=None, needsKw=False, templateArgs=[],
    response=200, contentType='text/html; charset=utf-8', headers={},
    requiresTailingSlash=False
    ):
    """
    a decorator that applies the result of the function to the provided template
    """
    self.__template=template
    self.__needsKw=needsKw
    self.__templateArgs=templateArgs
    self.__response=webAppResponses.get(response,"%d Unknown" % response)
    self.__contentType=contentType
    self.__headers=headers
    self.__requiresTailingSlash=requiresTailingSlash
    
  def __call__(self, func):
    def wrapper(*args, **kw):
      if self.__requiresTailingSlash and not kw.get('tailingSlash',False):
        raise redirectException(kw.get('script','')+kw.get('uri','')+'/')
      if args and isinstance(args[0], baseWebApp):
        t_kw=kw.copy()
        t_kw['webApp']=args[0]
      t_kw['templateArgs']=self.__templateArgs
      try:
        if self.__template:
          if self.__needsKw: r=self.__template(func(*args, **kw), **t_kw)
          else: r=self.__template(func(*args, **kw))
        else: r=func(*args, **kw)
      except: raise # TODO: handle error unless in debug mode
      s=kw['start_response']
      s(self.__response, [('content-type', self.__contentType)]+map(lambda k: (k,self.__headers[k]),self.__headers))
      if isinstance(r, basestring): return (r,)
      return r
    return wrapper

class baseWebApp:
  """
  The base for our web Application, it's a mini web framework
  """
  _mimeByExtension={
    'html': 'text/html', 'txt': 'text/plain', 'css': 'text/css',
    'js':'application/javascript',
    'png': 'image/png', 'gif': 'image/gif', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg'
  }

  def __init__(self, templatesDir, staticBaseDir={}, redirectBaseUrls={}, debug=False):
    """
    staticBaseDirs: a dictionary of prefixes and corresponding directories for serving static content
    redirectBaseUrls: just like staticBaseDirs, but redirect to this BaseUrls instead of surving them
    
    is a prefix is specified in both, redirectBaseUrls will be used.
    """
    self._templatesDir=templatesDir
    # TODO: add a self._templateFilesCache
    self._staticBaseDir={}
    # TODO: add a self._staticFilesCache
    self._debug=debug
    for k in staticBaseDir:
      v=staticBaseDir[k]
      if not os.path.isdir(v):
        print "** WARNING: directory [%s] not found, skipping" % v
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

  def _handelException(self, e, *args, **kw):
    s='_'+str(e.stat)
    if hasattr(self, s):
      return getattr(self, s)(e,*args, **kw)
    return self._genericException(e, *args, **kw)

  def _genericException(self, e, *args, **kw):
    r=webAppResponses.get(e.stat,"%d Unknown stat" % e.stat)
    if e.uri: s="exception [%s] happened when visiting [%s]" % (r,e.uri)
    else: s="exception [%s] happened" % r
    kw['start_response'](r, [('content-type', 'text/plain')])
    return [s]

  def _302(self, e, *args, **kw):
    r=webAppResponses[302]
    kw['start_response'](r, [
      ('content-type', 'text/plain'),('Location', e.kw['location'])
      ])
    return ("Redirect to "+ e.kw['location'],)

# you may customize exceptions like this
#  @expose(response=404,contentType='text/plain; charset=utf-8')
#  def _404(self, e, **kw):
#    if e.uri==None: return ('File is not found',)
#    return ('File [%s] is not found' % e.uri,)

  def __serveStatic(self, environ, start_response, uri, fn):
    """
    internal method to serve static files like png, css,js  ...etc.
    """
    if not os.path.exists(fn): raise fileNotFoundException(uri)
    try: f=open(fn,'rb')
    except IOError: raise fileNotFoundException(uri)

    ext=fn[fn.rfind('.'):][1:].lower()
    start_response("200 OK", [('content-type', self._mimeByExtension.get(ext,"application/octet-stream"))])
    # NOTE: since the file object is iteratable then no need for returning [r.read()]
    return f

  def __call__(self, environ, start_response):
    script=environ.get('SCRIPT_NAME','') # the uri of the webapp
    uri=environ['PATH_INFO'] # can be / or /view 
    try: cookies=SimpleCookie(environ.get('HTTP_COOKIE','')) # cookies['key'].value
    except: cookies=SimpleCookie('')
    if type(uri)!=unicode: uri=uri.decode('utf-8')
    if uri.endswith('/'): tailingSlash=True
    else: tailingSlash=False
    if uri.startswith('/'): uriList=uri[1:].split('/')
    else:  uriList=uri.split('/') # NOTE: this should never happen
    if uriList and uriList[-1]=='': uriList.pop()
    qs=environ.get('QUERY_STRING','')
    q=urlparse.parse_qs(qs)
    kw={
      'environ':environ, 'start_response':start_response,
      'script':script, 'uri':uri, 'tailingSlash':tailingSlash,
      'cookies':cookies, 'q':q,}
    if self._debug: print "** got ",uri
    if self._debug: print "** env= ",environ
    # FIXME: double check when do we need to decode/encode uri
    # check if we need to serve static content
    for k in self._staticBaseDirKeys:
      if uri.startswith(k):
        # SECURITY CHECK: that filename is really in side base filename ie. no ".." trick
        # NOTE: no need for this check as it seems to be done by paste
        bfn=self._staticBaseDir[k]
        fn=bfn+uri[len(k):]
        if not os.path.abspath(fn).startswith(bfn):
          return self._handelException(forbiddenException(),**kw)
        try: return self.__serveStatic(environ, start_response,
          uri, fn)
        except webAppBaseException as e:
          return self._handelException(e,**kw)
    # check if we need to serve redirect
    for k in self._redirectBaseUrlsKeys:
      if uri.startswith(k):
        u=self._redirectBaseUrls[k]+uri[len(k):]
        # FIXME: should we escape Location in start_response
        start_response("302 Temporary Redirect", [('Location',u),('content-type', 'text/html')])
        return [('<html><body><a href="%s">moved</a></body></html>' % escape(u))]
    if uriList and not uriList[0].startswith('_') and hasattr(self, uriList[0]):
      f=getattr(self, uriList[0])
      a=uriList[1:]
    else:
      f=self._root
      a=uriList
    try: r=f(*a, **kw)
    except webAppBaseException as e:
      return self._handelException(e,uri,**kw)
    return r

  @expose()
  def _root(self, *args, **kw):
    """
    called when no suitable method is found and it will be called for / too
    """
    return '''<html><body>You requested [<strong>%s</strong>]</body></html>'''% '/'.join(args)

def percentTemplate(v, **kw):
  # print kw
  d=kw['webApp']._templatesDir
  if not os.path.isdir(d): raise fileNotFoundException()
  args=kw.get('templateArgs',[])
  if args: bfn=args[0]
  else: bfn='root.html'
  fn=os.path.join(d, bfn)
  try: tmp=open(fn,'rt').read().decode('utf-8')
  except IOError: raise fileNotFoundException()
  except: print "**",fn; raise
  # NOTE: it expects a byte sequence not unicode object
  return [(tmp % v).encode('utf-8')]

if __name__ == '__main__':
    # this requires python-paste package
    from paste import httpserver
    app=baseWebApp(
      '/path/to/templates/files/',
      staticBaseDir={'/_files/':'/path/to/static/files/'}
    );
    # for options see http://pythonpaste.org/modules/httpserver.html
    httpserver.serve(app, host='127.0.0.1', port='8080')

