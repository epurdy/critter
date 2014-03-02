class Phonology(object):
  "Linguistic classification of phones."

  def __init__(self):
    self.vowels = set()
    self.consonants = set()
    self.stops = set()
    self.approximants = set()
    self.fricatives = set()
    self.nasals = set()
    self.voiceless = {'f', 's', 'th', 'sh', 'hh', 'v', 'p', 't', 'k'}
    self.short_vowels = {'ih', 'uh', 'eh', 'ah', 'ae', 'aa'}
    self._onsets = set()
    self._provisional_onsets = set()

  def read(self, dict_file):
    for line in dict_file:
      phone, category = line.lower().split()
      if category == 'vowel':
        self.vowels.add(phone)
      else:
        if category != 'semivowel':
          self.consonants.add(phone)
	if category == 'stop':
	  self.stops.add(phone)
        elif category in ('semivowel', 'liquid'):
          self.approximants.add(phone)
        elif category in ('fricative', 'aspirate'):
          self.fricatives.add(phone)
        elif category == 'nasal':
          self.nasals.add(phone)

  def is_legal_onset(self, seq, follow):
    if not self._onsets:
      self._onsets |= {(c,) for c in (self.consonants | {'y', 'w'}) - {'ng'}}
      self._onsets |= {(s, a) for s in self.stops
                              for a in self.approximants - {'y'}}
      self._onsets |= {(f, a) for f in self.fricatives & self.voiceless
                              for a in self.approximants - {'y'}}
      self._onsets |= {('s', s) for s in self.stops & self.voiceless}
      self._onsets |= {('s', n) for n in self.nasals - {'ng'}}
      self._onsets |= {('s', f) for f in self.fricatives & self.voiceless}
      self._onsets |= {('s', s, a) for s in self.stops & self.voiceless
                                   for a in self.approximants}
      self._onsets |= {('s', f, a) for f in self.fricatives & self.voiceless
                                   for a in self.approximants}
      self._provisional_onsets |= {(c, 'y') for c in self.consonants}
    return ((tuple(seq) in self._onsets) or
            (tuple(seq) in self._provisional_onsets and
             (follow[:1] == ['uw'] or follow[:2] == ['uh', 'r'])))

if __name__ == '__main__':
  ph = Phonology()
  with open('cmudict.0.7a.phones') as f:
    ph.read(f)
  assert ph.is_legal_onset(('n', 'y'), ('uh', 'r'))
  assert ph.is_legal_onset(('n', 'y'), ('uw',))
  assert not ph.is_legal_onset(('n', 'y'), ('ah',))
