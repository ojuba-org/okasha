# -*- coding: utf-8 -*-
import sys, os, os.path
from test import webApp
d='/path/to/sample/prefix'
application=webApp(
  'SafeMode',
  os.path.join(d,'templates'),
  staticBaseDir={'/_files/':os.path.join(d,'files')}
);

