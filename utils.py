# coding=utf8
# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import time, datetime
import os

iso6709 = re.compile(r'((\+|-)[0-9]*.[0-9]*)((\+|-)[0-9]*.[0-9]*)')
def decodeIso6709(strLoc):
  match = iso6709.fullmatch(strLoc)
  return (float(match.group(1)), float(match.group(3)))

def currentPosixTime():
  d = datetime.datetime.now()
  return time.mktime(d.timetuple())

def floatToStr(f, plus=False):
  if f >= 0:
    return ('+' if plus else '') + str(f)
  else:
    return str(f)

def keywordString(keywords):
  pieces = []
  for keyword in keywords:
    pieces.append(keyword + '=' + keywords[keyword])
  return '&'.join(pieces)

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)