import numpy as np 
import dictionaries


# if we know the number of syllables, we can sort of find syllables
# using dynamic programming
def get_splits(words, moby_dict, pronunciation_dict, testing=False):
  rv = {}

  words = [ x.lower() for x in words ]

  counts = {}
  sub_counts = {}
  unseen_counts = {}
  for word in moby_dict:
    for l in [2]: # xrange(1,5):
      for i in xrange(len(word)):
        if i + l >= len(word): 
          break
        part = word[i:i+l]
        subsyl = False
        for syl in moby_dict[word]:
          if part in syl:
            subsyl = True
        if not subsyl:
          if part in unseen_counts:
            unseen_counts[part] += 1
          else:
            unseen_counts[part] = 1

    for part in moby_dict[word]:
      if part in counts:
        counts[part] += 1
      else:
        counts[part] = 1

  if testing:
    nhits, ntot = 0, 0

  for word in words:
    if word in rv: 
      continue

    vowels = [ x for x in pronunciation_dict[word] if x[-1] in '012' ]
    nsyls = len(vowels)

    # tab[i,j] is minimum cost of parsing characters 0:i as j syllables
    tab = np.zeros((len(word)+1, nsyls+1)) + np.inf
    tab[0,0] = 0
    parent = {}
    parent[0,0] = None
    for i in xrange(1,len(word)+1):
      for j in xrange(1,nsyls+1):
        for k in xrange(i):
          cost = (tab[k,j-1] 
                  - np.log(counts.get(word[k:i], 0.0000000000001)))
          for l in xrange(k,i):
#            for m in xrange(l+1,i):
            m = l+2
            if m > i: break
#              cost -=  np.log(sub_counts.get(word[l:m], 0.0000000000001))
            cost +=  np.log(unseen_counts.get(word[l:m], 0.0000000000001))
          if cost < tab[i,j]:
            tab[i,j] = cost
            parent[i,j] = k

    try:
      finger = len(word)
      parts = []
      for i in xrange(nsyls,0,-1):
        parts.append(word[parent[finger,i]:finger])
        finger = parent[finger,i]
      parts.reverse()
    except:
      print 'Parsing failed for', word

    rv[word] = parts

    if testing:
      if parts == moby_dict[word]:
        nhits += 1
      else:
        print parts, moby_dict[word]
      ntot += 1
      print nhits, '/', ntot, '=', float(nhits)/ntot

  return rv

if __name__ == '__main__':
  import dictionaries
  cmu_dict = dictionaries.read_cmu_dict()
  moby_dict = dictionaries.read_moby_dict()

  words = [ word for word in moby_dict.keys() if word in cmu_dict ]
  get_splits(words, moby_dict, cmu_dict, True)

