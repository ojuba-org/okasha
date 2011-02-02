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
    return self._tmp.render(**o)


