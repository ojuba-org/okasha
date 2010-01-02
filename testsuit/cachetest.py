#! /usr/bin/python
# -*- coding: utf-8 -*-
import sys, os, os.path, time

print 

try:
  from okasha.utils import ObjectsCache
except ImportError:
  try: 
    sys.path.insert(0,os.path.abspath(os.curdir))
    from okasha.utils import ObjectsCache
  except ImportError:
    sys.path.insert(0,os.path.abspath(os.path.join(os.curdir,'..')))
    from okasha.utils import ObjectsCache

ch=ObjectsCache(lock=None, minCount=10, maxCount=100, maxTime=0)
print "asserting empty start: ",
assert(len(ch.objs)==0)
print "OK"

print "asserting respecting minCount: ",
for i in range(10):
  ch.append(i,i)
  assert(len(ch.objs)==i+1)
print "OK, after inserting 10 objects we have ", len(ch.objs), " cached"

print "asserting getting least expected while below minCount: ",
ch=ObjectsCache(lock=None, minCount=10, maxCount=100, maxTime=0)
for i in range(10):
  ch.append(i,100-3*i)
  for j in range(i+1):
    assert(ch.get(j)==100-3*j)
print "OK"


print "asserting getting while below minCount: ",
ch=ObjectsCache(lock=None, minCount=10, maxCount=100, maxTime=0)
for i in range(10):
  ch.append(i,100-3*i)
  for j in range(i,-1,-1):
    assert(ch.get(j)==100-3*j)
print "OK"

print "asserting below maxCount: ",
ch=ObjectsCache(lock=None, minCount=10, maxCount=100, maxTime=0)
for i in range(100):
  ch.append(i,3*i)
  for j in range(i+1):
    assert(ch.get(j)==3*j)
print "OK"

print "asserting above maxCount (132 objs in 100 max): ",
ch=ObjectsCache(lock=None, minCount=10, maxCount=100, maxTime=0)
maxmissing=0
for i in range(132):
  #print "inserting id=", i,", value=",3*i
  ch.append(i,3*i)
  missing=0
  for j in range(i+1):
    #print "** j=",j,", ids=", map(lambda o:o.objId, ch.objs),", objs=",map(lambda o:o.obj, ch.objs)
    v=ch.get(j)
    assert(v==3*j or v==None)
    if v==None: missing+=1
  maxmissing=max(missing,maxmissing)
assert(maxmissing<=32)
print "OK, we are keeping ", len(ch.objs), " objects and the maximum missing=",maxmissing


import random
random.seed(time.time())
print "random testing: "
# insert 5 values then choose randomly between getting or inserting
# when in getting mode, choose a random number of how many times to repeat getting the same id

#ch.append(objId, obj)
