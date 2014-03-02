import operator
from phonology import Phonology
from itertools import combinations, tee, izip

def parse_cmudict(dict_file, phonology):
  """Parses the CMU phonetic dictionary word file into a dict mapping words to
     phonetically spelled syllables."""
  words = {}
  word_starts = {'\''} | {chr(ord('a') + c) for c in range(26)}
  for line in dict_file.readlines():
    line = line.lower()
    if not line[0] in word_starts:
      continue
    if '(' in line:
      continue
    word, phones = line.strip().split(None, 1)
    words[word] = build_syllables(phones.split(), phonology)
  return words

def build_syllables(phones, phonology):
  "Splits phones with stress marks into conventional syllables."
  plain_phones = [(ph[:-1] if ph[-1] in '012' else ph) for ph in phones]
  nuclei = [i for i, ph in enumerate(phones) if ph[-1] in '012']
  syllables = []
  for i, j in pairwise([-1] + nuclei + [-1]):
    if i == -1:
      coda, next_onset = [], phones[:j]
    elif j == -1:
      coda, next_onset = phones[i + 1:], []
    else:
      for k in range(i + 1, j):
        candidate, follow = plain_phones[k:j], plain_phones[j:j + 2]
        unreduced_short_vowel = (phones[k - 1][-1] in '12' and
            plain_phones[k - 1] in phonology.short_vowels)
        if (phonology.is_legal_onset(candidate, follow) and
            not unreduced_short_vowel):
          coda, next_onset = phones[i + 1:k], phones[k:j]
          break
      else:
        coda, next_onset = phones[i + 1:j], []
    if i != -1:
      syllables.append(tuple(onset + [plain_phones[i]] + coda))
    onset = next_onset
  return tuple(syllables)

def pairwise(iterable):
  "s -> (s0,s1), (s1,s2), (s2, s3), ..."
  a, b = tee(iterable)
  next(b, None)
  return izip(a, b)

def spell_syllables(word, phone_syllables, phonology):
  "Splits word into spelled syllables given phonetic splits."
  num_syllables = len(phone_syllables)
  if num_syllables == 1: return (word,)
  candidates = []
  for splits in combinations(range(1, len(word)), num_syllables - 1):
    parts = [word[start:end] for start, end in
             pairwise((0,) + splits + (len(word),))]
    scores = [score_spelling(part, syllable, phonology)
              for part, syllable in zip(parts, phone_syllables)]
    score = reduce(operator.mul, scores)
    if score > .1:
      candidates.append((score, tuple(parts)))
  if candidates:
    syl = list(max(candidates)[1])
    # Split up double consonants.
    for i in range(len(syl) - 1):
      if (len(syl[i]) > 2 and syl[i][-1] == syl[i][-2] and
          syl[i][-1] not in 'aeiou'):
        syl[i], syl[i + 1] = syl[i][:-1], syl[i][-1] + syl[i + 1]
    for i in range(1, len(syl)):
      if (len(syl[i]) > 2 and syl[i][0] == syl[i][1] and
          syl[i][0] not in 'aeiou'):
        syl[i - 1], syl[i] = syl[i - 1] + syl[i][0], syl[i][1:]
    return tuple(syl)

def score_spelling(letters, phones, phonology):
  "Rates the plausibility of letters as a spelling for phones."
  odds = 1
  if len(letters) < len(phones):
    odds *= 0.1
  letter_sig = vowel_signature(letters, phonology)
  phone_sig = vowel_signature(phones, phonology)
  if letter_sig == phone_sig:
    odds *= 2.0
  else:
    odds *= .5
  if sound_mismatch(letters, phones):
    odds *= 0.01
  return odds

sounds = {'p': 'p', 't': 't', 'g': 'g', 'n': 'n', 'l': 'l', 'm': 'm'}
def sound_mismatch(letters, phones):
  "Returns true for obvious sound disagreements between letters and phones."
  letter_bag = set(letters)
  phone_bag = set(phones)
  return any(phone in phone_bag and not letter in letter_bag
             for phone, letter in sounds.iteritems())

def vowel_signature(seq, phonology):
  "Marks transitions and order of vowels and non-vowels."
  vowel, consonant = range(2)
  signature = [-1]
  for elem in seq:
    if elem == 'er':
      if signature[-1] != vowel:
        signature.append(vowel)
        signature.append(consonant)
    elif elem in 'aeiou' or elem in phonology.vowels:
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
  
  phonology = Phonology()
  with open('cmudict.0.7a.phones') as f:
    phonology.read(f)
  with open('cmudict.0.7a') as f:
    phone_dict = parse_cmudict(f, phonology)

  assert phone_dict['comma'] == (('k', 'aa', 'm'), ('ah',))
  assert phone_dict['command'] == (('k', 'ah'), ('m', 'ae', 'n', 'd'))
  assert phone_dict['procurer'] == (('p', 'r', 'ow'),
                                    ('k', 'y', 'uh', 'r'), ('er',))

  nhits, ntot = 0, 0
  for word, phones in phone_dict.iteritems():
    #print word, phones
    if len(phones) == 0: continue
    if len(word) > 20: continue
    syllables = spell_syllables(word, phones, phonology)
    if word.lower() in moby_dict:
      #print word, phones, syllables
      #print moby_dict[word.lower()]
      if syllables == tuple(moby_dict[word.lower()]):
        nhits += 1
      else:
        print word, phones, syllables
        print moby_dict[word.lower()]
      ntot += 1
      print nhits, '/', ntot, float(nhits) / ntot
