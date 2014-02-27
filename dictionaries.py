import re

def valid_char(c):
  c = c.lower()
  if 'a' <= c <= 'z':
    return True
  if c == "'":
    return True
  return False

def combine_dicts(*ds):
  rv = {}
  for d in ds:
    for key in d:
      rv[key] = d[key]
  return rv

def read_cmu_dict():
  filenames = ['cmudict.0.7a', 'hamlet_words']
  d = {}
  for filename in filenames:
    f = open(filename)
    for line in f:
      line = line.strip()
      if not line: 
        continue
      if line[0] == '#':
        continue
      parts = line.split()
      if not valid_char(parts[0][0]):
        continue
      d[parts[0].lower()] = parts[1:]
    f.close()

  return d

def read_moby_dict():
  filenames = ['mhyph.txt']
  split_re = re.compile('[- \xa5]')
  d = {}
  for filename in filenames:
    f = open(filename)
    for line in f:
      line = line.strip()
      if not line:
        continue
      if line[0] == '#':
        continue
      parts = re.split(split_re, line)
      parts = [ part.lower() for part in parts ]
      d[''.join(parts)] = parts
    f.close()
  return d

def read_google_dict():
  filenames = ['google_splits']
  split_re = re.compile('[- ]|\xc2\xb7')
  d = {}
  for filename in filenames:
    f = open(filename)
    for line in f:
      line = line.strip()
      if not line:
        continue
      if line[0] == '#':
        continue
      parts = re.split(split_re, line)
      parts = [ part.lower() for part in parts ]
      d[''.join(parts)] = parts
    f.close()
  return d

def read_split_dict():
  filenames = ['split_dict']
  d = {}
  for filename in filenames:
    f = open(filename)
    for line in f:
      line = line.strip()
      if not line:
        continue
      if line[0] == '#':
        continue
      parts = line.split()
      d[parts[0].lower()] = parts[1:]
    f.close()
  return d
