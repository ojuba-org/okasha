# -*- coding: UTF-8 -*-
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

this is integrates bottle's SimpleTemplate into okasha
for details and sytax visit http://bottle.paws.de/docs/dev/stpl.html
"""

import sys, os, os.path
from baseWebApp import fileNotFoundException
from bottleTemplateSegment import SimpleTemplate, TemplateError

class ThDict(dict):
  """
  a dictionary that can be accessed through mydict.key
  constructor takes an extra argument that is the default value

  you can't set values for the following keys:
'iteritems', 'pop', 'has_key', 'viewkeys', 'viewitems', 'itervalues', 'get', 'keys', 'update', 'popitem', 'copy', 'iterkeys', 'fromkeys', 'setdefault', 'viewvalues', 'items', 'clear', 'values'

  example usage:
mydict=ThDict(None, {"y":3})
print mydict.x
print mydict.y
mydict.y=2
mydict.x=7
print mydict.x
print mydict.y
  """
  def __init__(self, default=None, *a, **kw):
    self.__dict__["_default"]=default
    dict.__init__(self, *a, **kw)
    self.__dict__["_protect"] = set(dir(self))
    self._protect.add("_protect")
    #print filter(lambda s: not s.startswith('_'), self._protect)
  def __getattr__(self, key):
    return self.get(key, self._default)
  def __setattr__(self, k, v):
    if k in self._protect: raise KeyError
    self[k]=v
    return v
  def __delattr__(self, key):
    if self.has_key(key): del self[key]
    return super(dict).__delattr__(key)

class bottleTemplate(object):
  def __init__(self, *a, **kw):
    self._tmp=None

  def _load(self, rq, bfn=None, **kw):
    if hasattr(rq.webapp._templatesDir, '__iter__'): d=rq.webapp._templatesDir
    else: d=[rq.webapp._templatesDir]
    if not bfn: bfn='root.tpl'
    try: self._tmp=SimpleTemplate(name=bfn, lookup=d)
    except:
      rq.webapp._logger.debug('template error fn=[%s]' % bfn)
      raise
    # FIXME: check for valid template

  def __call__(self, rq, o, *a, **kw):
    if not self._tmp: self._load(rq, *a, **kw)
    o.update(kw)
    return self._tmp.render(_kw=ThDict(None,o), **o)


