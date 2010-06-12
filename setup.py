#! /usr/bin/python
from distutils.core import setup
from glob import *
import os, sys
# to install type: 
# python setup.py install --root=/

# do the install
setup (name='okasha', version='0.1.0',
      description='trivial WSGI web framework for python',
      author='Muayyad Saleh Alsadi',
      author_email='alsadi@ojuba.org',
      url='http://git.ojuba.org/cgit/okasha/about/',
      license='Waqf',
      packages=['okasha'],
      data_files=[]
)

