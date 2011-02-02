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
import sys, os, os.path, threading
from lxml import etree
from utils import ObjectsCache # kid has its own cache

from baseWebApp import fileNotFoundException

xsltCache=ObjectsCache(lock=threading.Lock())

def xsltTemplate(rq, o, bfn=None, **kw):
  """
  
  """
  fn=rq.webapp._getTemplateFile(bfn, default="root.xsl")
  # prepare xsl trans
  trans=xsltCache.get(fn)
  if not trans:
    try: xslt_doc=etree.parse(fn)
    except IOError: raise fileNotFoundException()
    except:
      # FIXME: check for valid template # lxml.etree.XMLSyntaxError:
      rq.webapp._logger.debug('template error fn=[%s]' % fn)
      raise
    trans = etree.XSLT(xslt_doc)
    xsltCache.append(fn, trans)
  # prepare object
  if isinstance(o,basestring):
    doc=etree.fromstring(o)
  else: doc=o
  r = trans(doc, **kw)
  return etree.tostring(r, encoding='UTF-8' , pretty_print=True)

