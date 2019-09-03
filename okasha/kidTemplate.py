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

"""
import sys, os, os.path
import kid
from .baseWebApp import fileNotFoundException
#from utils import ObjectsCache # kid has its own cache

def kidTemplate(rq, o, bfn=None, **kw):
  fn=rq.webapp._getTemplateFile(bfn, default="root.kid")
  try: tmp=kid.load_template(file=fn)
  except kid.template_util.TemplateNotFound: raise fileNotFoundException()
  except:
    rq.webapp._logger.debug('template error fn=[%s]' % fn)
    raise
  # FIXME: check for valid template
  o.update(kw)
  s=tmp.Template(**o).serialize()
  return s

