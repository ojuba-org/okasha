#! /usr/bin/python
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

from okasha.baseWebApp import *
import json

class webApp(baseWebApp):
  def __init__(self, mode,*args, **kw):
    """
    mode is just an argument to show how to recive arguments
    """
    self.mode=mode
    baseWebApp.__init__(self,*args, **kw)

  @expose()
  def verbatim(self, *args, **kw):
    """
    this is an example of sending a verbatim html code as-is
    to test it visit http://localhost:8080/verbatim/some/args/?id=5
    """
    return """<html><body style="background:url('/_files/logo.gif') top right no-repeat;">
<h1>welcome to verbatim html from python</h1>
You requested [<strong>%s</strong>]<br/>
You query is [<strong>%s</strong>]<br/>
</body></html>""" % (escape('/'.join(args)), escape(kw['q'].__repr__()))

  @expose()
  def _root(self, *args, **kw):
    """
    this is called when / or when no other suitable method is found
    you could just redirect to /index for example or raise fileNotFoundException()
    """
    return """<html><body>
<h1>welcome to Okasha</h1>
You requested [<strong>%s</strong>] which is not handled by any method<br/>
You query is [<strong>%s</strong>]<br/>
<h2>try out the following</h2>
<ul>
<li><a href="http://localhost:8080/verbatim/some/args/?id=5">verbatim</a></li>
<li><a href="http://localhost:8080/tmp/some/args/?id=5">tmp</a></li>
<li><a href="http://localhost:8080/tmp/err/raised/?id=5">tmp (not allowed)</a></li>
<li><a href="http://localhost:8080/moved/">redirects</a></li>
<li><a href="http://localhost:8080/main/">main</a></li>
</ul>
</body></html>""" % (escape('/'.join(args)), escape(kw['q'].__repr__()))

  @expose(percentTemplate,True,["tmp.html"])
  def tmp(self, *args, **kw):
    """
    this is how you can use simple % formatting templates,
    just return a dictionary, and it will be applied to the named template.
    to test it visit
      http://localhost:8080/tmp/some/args/?id=5
      http://localhost:8080/tmp/err/raised/?id=5
    """
    if args and args[0]=='err': raise forbiddenException()
    return {
      'title':'Okasha simple templates',
      'key1':'val1','key2':'val2','args':'/'.join(args)
      }

  def moved(self, *args, **kw):
    """
    this is an example of using redirects
    to test it visit http://localhost:8080/moved/
    """
    raise redirectException(kw.get('script','')+'/main/')


  @expose(percentTemplate,True,["main.html"])
  def main(self, *args, **kw):
    """
    this is an example of using ajax/json
    also notice that we can access to class properties
    to test it visit http://localhost:8080/main/
    """
    return {
      'title':'Okasha: sample web application',
      'script':kw.get('script',''),
      'mode':self.mode, 'version':'0.1.0'
      }

  @expose(json.dumps,contentType='application/x-javascript; charset=utf-8')
  def ajaxGet(self, *args, **kw):
    """
    this is an example of using ajax/json
    to test it visit http://localhost:8080/ajaxGet"
    """
    import time, random
    return {'time':time.time(),'rnd':random.randrange(1,7)}

  @expose(json.dumps,contentType='application/x-javascript; charset=utf-8')
  def ajaxToUpper(self, *args, **kw):
    """
    this is an example of using ajax/json
    to test it visit http://localhost:8080/ajaxToUpper?text="LowerCaseMe"
    """
    t=kw['q'].get('text',[''])[-1]
    return t.upper()

  @expose(json.dumps,contentType='application/x-javascript; charset=utf-8')
  def ajaxSplit(self, *args, **kw):
    """
    this is an example of using ajax/json
    to test it visit http://localhost:8080/ajaxSplit?text=12-345-678&by=-
    """
    t=kw['q'].get('text',[''])[-1]
    d=kw['q'].get('by',[''])[-1]
    return t.split(d)

# you may customize exceptions like this
#  @expose(response=404,contentType='text/plain; charset=utf-8')
#  def _404(self, e, **kw):
#    if e.uri==None: return ('File is not found',)
#    return ('File [%s] is not found' % e.uri,)

if __name__ == '__main__':
    # this requires python-paste package
    import logging
    from paste import httpserver
    import sys, os, os.path
    
    myLogger=logging.getLogger('MyTestWebApp')
    h=logging.StreamHandler() # in production use WatchedFileHandler or RotatingFileHandler
    h.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    myLogger.addHandler(h)
    myLogger.setLevel(logging.DEBUG) # in production use logging.INFO
    
    d=os.path.dirname(sys.argv[0])
    app=webApp(
      'SafeMode',
      os.path.join(d,'templates'),
      staticBaseDir={'/_files/':os.path.join(d,'files')},
      logger=myLogger
    );
    # for options see http://pythonpaste.org/modules/httpserver.html
    httpserver.serve(app, host='127.0.0.1', port='8080')

