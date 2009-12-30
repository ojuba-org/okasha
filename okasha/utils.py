# -*- coding: utf-8 -*-
"""

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
import time
import bisect
from itertools import groupby,imap
# TODO: is this needed ?
def unixUniq(l):
  """
  Unix-like uniq, the iteratable argument should be sorted first to get unique elements.
  """
  return imap(lambda j:j[0],groupby(l,lambda i: i))

def unixUniqAndCount(l):
  """
  Unix-like uniq -c, it returns an iteratable of tuples (count, uniq_entry)
  """
  return imap(lambda j:(len(list(j[1])),j[0]),groupby(l,lambda i: i))

class ObjectsCacheObject:
  def __init__(self, objId, obj):
    self.objId=objId
    self.obj=obj
    self.atime=self.ctime=time.time()

  def __cmp__(self, b):
    if isinstance(b,ObjectsCacheObject): b=b.atime
    return cmp(self.atime,b)

class ObjectsCache:
  def __init__(self, minCount=10, maxCount=100, maxTime=3600):
    """
    minCount is the minimum number of cached objects below which no cached object will be freed, use 0 to set no lower limit
    maxCount is the maximum number of cached objects above which no cached object will be kept, use 0 to set no upper limit
    maxTime is positive time to live in seconds, all objects older than this will be removed when free is called, use 0 to discard time checking
    
    example:
      setting minCount and maxTime to 0 will keep all cached objects no matter how many or for how long
      setting maxCount to 0 will disable caching (all objects will be freed when free is called)
    """
    self.maxTime=maxTime
    self.maxCount=maxCount
    self.minCount=minCount
    self.objs=[]
    self._hash={}
    self._shift=0

  def get(self, objId):
    self.free()
    i=self._hash.get(objId,None)
    if i==None: return None
    o=self.objs[i+self._shift]
    o.atime=time.time()
    return o.obj

  def append(self, objId, obj):
    self.free()
    self._hash[objId]=len(self.objs)-self._shift
    self.objs.append(ObjectsCacheObject(objId, obj))

  def free(self):
    """
    free old objects, return number of freed objects
    """
    l=len(self.objs)
    if self.minCount>0 and l<=self.minCount: return 0
    k=l-self.minCount # max number of objs to remove
    j=max(l-self.maxCount,0) # number of objs to remove
    if self.maxTime>0:
      c=time.time()-self.maxTime
      i=bisect.bisect(self.objs,c) # number of objs to remove by time
      i=max(i,j)
    else: i=j
    if self.minCount>0: i=min(j,k)
    # can be done by deleting hash elements which has values < -newshift
    for o in self.objs[:i]: del self._hash[o.objId]
    del self.objs[:i]
    self._shift-=i
    return i

