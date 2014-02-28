import numpy as np

import dictionaries

def alignment(word, pronunciation):
  phones = []
  for phone in pronunciation:
    if phone[-1] in '012':
      phones.append(phone[:-1])
    else:
      phones.append(phone)
  phones = tuple(phones)

  max_len = 8

  # tab[i,j] is the cost of matching word[:i] to phones[:j]
  tab = np.zeros( (len(word)+1, len(pronunciation)+1) ) + np.inf
  tab[0,0] = 0
  parent = {}
  parent[0,0] = None
  for i in xrange(len(word)+1):
    for j in xrange(len(phones)+1):
      for k in xrange(max(i-max_len,0) ,i+1):
        for l in xrange(max(j-max_len,0), j+1):
          if k == i and l == j: continue
          cost = tab[k,l] + match_dict.get((word[k:i], phones[l:j]), 
                                           1000.0 * max(1,(i-k)))
          assert len(word[k:i]) == i-k
          assert len(phones[l:j]) == j-l
          if cost < tab[i,j]:
            tab[i,j] = cost
            parent[i,j] = (k,l)

  correspondences = []
  finger = len(word), len(phones)
  while finger is not None:
    new_finger = parent[finger]
    if new_finger is not None:
      correspondences.append( 
        (word[new_finger[0]:finger[0]], phones[new_finger[1]:finger[1]]))
    if (new_finger is not None 
        and tab[new_finger] < 1000.0 and tab[finger] >= 1000.0):
      print 'XXX', word[new_finger[0]:finger[0]], phones[new_finger[1]:finger[1]]
    finger = new_finger
  correspondences.reverse()
  if tab[len(word), len(phones)] >= 1000.0:
    print 'XXX', word
    print 'XXX', phones
    print 'XXX', correspondences
    print 'XXX'
  return correspondences

moby_dict = dictionaries.read_moby_dict()
cmu_dict = dictionaries.read_cmu_dict()
match_dict = dictionaries.read_match_dict()
exceptions = dictionaries.read_exceptions_dict()

words = [ word for word in moby_dict if word in cmu_dict ]

print len(words)
assert False
for word in words:
  if word in exceptions: 
    print 'EXCEPTION', word
    continue
  print word
  print moby_dict[word]
  print cmu_dict[word]
  correspondences = alignment(word, cmu_dict[word])
  print correspondences
