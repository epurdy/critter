import operator
from itertools import combinations, tee, izip

vowel, consonant = range(2)

def read_phone_vowels(phones_file):
  "Reads which phones in the CMU phonetic dictionary are vowels."
  vowels = set()
  for line in phones_file.readlines():
    phone, category = line.lower().split()
    if category == 'vowel':
      vowels.add(phone)
  return vowels

def parse_cmudict(dict_file, vowels):
  """Parses the CMU phonetic dictionary word file into a dict mapping words to
     phonetically spelled syllables."""
  words = {}
  word_starts = set('\'') | set(chr(ord('a') + c) for c in range(26))
  for line in dict_file.readlines():
    line = line.lower()
    if not line[0] in word_starts:
      continue
    if '(' in line:
      continue
    word, phones = line.strip().split(None, 1)
    words[word] = build_syllables(phones.split(), vowels)
  return words

def build_syllables(phones, vowels):
  "Splits phones with stress marks into conventional syllables."
  syllables = []
  # Syllable structure is onset(consonant) + nucleus(vowel) + coda.
  # Assume the nucleus is always a stressed vowel, and prefer to bind
  # at least one consonant in the nucleus over appending to the coda.
  onset = []
  coda = []
  nucleus = None
  for ph in phones:
    if ph[-1] in '012':
      if nucleus:
        next_onset = ([coda.pop()] if coda else [])
        syllables.append(tuple(onset + [nucleus] + coda))
        onset = next_onset
        coda = []
      nucleus = ph[:-1]
    elif nucleus:
      coda.append(ph)
    else:
      onset.append(ph)
  if nucleus:
    syllables.append(tuple(onset + [nucleus] + coda))
  return tuple(syllables)

def pairwise(iterable):
  "s -> (s0,s1), (s1,s2), (s2, s3), ..."
  a, b = tee(iterable)
  next(b, None)
  return izip(a, b)

def spell_syllables(word, phonetic_syllables, vowels):
  "Splits word into spelled syllables given phonetic splits."
  num_syllables = len(phonetic_syllables)
  if num_syllables == 1: return (word,)
  candidates = []
  for splits in combinations(range(1, len(word)), num_syllables - 1):
    parts = [word[start:end] for start, end in
             pairwise((0,) + splits + (len(word),))]
    scores = [score_spelling(part, syllable, vowels)
              for part, syllable in zip(parts, phonetic_syllables)]
    score = reduce(operator.mul, scores)
    if score > .1:
      candidates.append((score, tuple(parts)))
  if candidates:
    return max(candidates)[1]

def score_spelling(letters, phones, vowels):
  "Rates the plausibility of letters as a spelling for phones."
  odds = 1
  if len(letters) < len(phones):
    odds *= 0.1
  if vowel_signature(letters, vowels) == vowel_signature(phones, vowels):
    odds *= 2.0
  else:
    odds *= .5
  return odds

def vowel_signature(seq, vowels):
  "Marks transitions and order of vowels and non-vowels."
  signature = [-1]
  for elem in seq:
    if elem == 'er':
      if signature[-1] != vowel:
        signature.append(vowel)
        signature.append(consonant)
    elif elem in vowels:
      if signature[-1] != vowel:
        signature.append(vowel)
    else:
      if signature[-1] != consonant:
        signature.append(consonant)
  return signature[1:]

if __name__ == '__main__':
  import dictionaries
  import splitting
  moby_dict = dictionaries.read_moby_dict()
  

  vowels = set('aeiou')
  with open('cmudict.0.7a.phones') as f:
    vowels |= read_phone_vowels(f)
  with open('cmudict.0.7a') as f:
    phone_dict = parse_cmudict(f, vowels)

  nhits, ntot = 0, 0
  for word, phones in phone_dict.iteritems():
    print word, phones
    if len(phones) == 0: continue
    if len(word) > 20: continue
    syllables = spell_syllables(word, phones, vowels)
    if word.lower() in moby_dict:
      print word, phones, syllables
      print moby_dict[word.lower()]
      if syllables == tuple(moby_dict[word.lower()]):
        nhits += 1
      ntot += 1
      print nhits, '/', ntot, float(nhits) / ntot
