from nltk.tokenize import regexp_tokenize
import itertools, sys, random, cmd, re
import editor, dictionaries, splitting


def clean(w):
  return ''.join(c for c in w if dictionaries.valid_char(c))

punctuation = '\'.!?,-:;'

contract = dict(of="f'", the="th'", to="t'")

stop_words = ['to', 'or', 'is', 'and', 'in']

def tokenize(s):
  tokens = regexp_tokenize(s, pattern='[a-zA-Z\']+|,|\.|:|!|\?')
  return tokens

class Reading:
  UNVOICED = 0
  UNSTRESSED = 1
  STRESSED = 2
  UNKNOWN = 3

def mark_word_with_reading(word, reading):
#  split = split_dict[word.lower()]
  if len(reading) == 1:
    split = [word.lower()]
  else:
    try:
      split = split_dict[word.lower()]
    except:
      print
      print "Don't know how to split the word '%s' into syllables" % word.lower()
      print 'Giving up...'
      sys.exit()

  marked_word = ''
  marked_syllables = []
  for i, (part, syl) in enumerate(zip(split, reading)):
    if syl == Reading.UNVOICED:
      if part.lower() not in contract:
        marked_syl = '<%s>' % part.lower()
      else:
        if i+1 < len(split) and syl[i+1] == Reading.STRESSED:
          marked_syl = contract[part.lower()].upper()
        else:
          marked_syl = contract[part.lower()]
    elif syl == Reading.UNSTRESSED:
      marked_syl = part.lower()
    elif syl == Reading.STRESSED:
      marked_syl = part.upper()
    else:
      raise Exception
    marked_word += marked_syl
    marked_syllables.append(marked_syl)

  return marked_word, marked_syllables + [' ']

def mark_line_with_reading(tokens, dictionary_reading, reading):
  marked_tokens = []
  marked_syllables = []
  start = 0
  word_idx = 0
  for t in tokens:
    if t in punctuation:
      marked_tokens.append(t)
      marked_syllables.extend([t, ' '])
      continue
    end = start + len(dictionary_reading[word_idx])
    marked_word, marked_word_syllables = mark_word_with_reading(t, reading[start:end])
    marked_tokens.append(marked_word)
    marked_syllables.extend(marked_word_syllables)
    start = end
    word_idx += 1

  return marked_tokens, marked_syllables

def get_dictionary_reading(word):
  word = word.lower()

  if word in stop_words: return [Reading.UNSTRESSED]

  try:
    pronounce = cmu_dict[word]
  except KeyError:
    print
    print "Don't know how to pronounce this word:", word
    print 'Giving up...'
    sys.exit()
  said_vowels = [ part for part in pronounce if part[-1] in '012' ]

  if len(said_vowels) == 1:
    return [Reading.UNKNOWN]

  syllables = []
  for v in said_vowels:
    if v[-1] == '0':
      syllables.append(Reading.UNSTRESSED)
    elif v[-1] == '1':
      syllables.append(Reading.STRESSED)
    else:
      syllables.append(Reading.UNKNOWN)
  return syllables

def get_words(data):
  tokens = tokenize(data)
  words = [ t for t in tokens if t not in punctuation ] 
  return words

def infer_reading(data):
  tokens = tokenize(data)
  words = [ t for t in tokens if t not in punctuation ] 
  dictionary_reading = [ get_dictionary_reading(w) for w in words ]
  flat_dictionary_reading = sum(dictionary_reading, [])
  nsyls = len(flat_dictionary_reading)

  best_score = 100000
  best_reading = None
  if 15 <= nsyls <= 20:
    print 'This may take awhile, since we are using a stupid algorithm.'
  if nsyls > 20:
    print
    print 'This line:', data
    print 'has too many syllables for the stupid algorithm we are using right now!'
    print 'Giving up...'
    sys.exit()
  for reading in itertools.product(*((
        [Reading.UNVOICED, Reading.UNSTRESSED, Reading.STRESSED],) * nsyls)):
#    print ' '.join(mark_line_with_reading(tokens, dictionary_reading, reading))
    score = 0
    for syl in reading:
      if syl == Reading.UNVOICED:
        score += 8
    for syl, dict_syl in zip(reading, flat_dictionary_reading):
      if syl != dict_syl:
        score += 10
    if reading[0] != Reading.UNSTRESSED:
      score += 5
    for (asyl, bsyl) in zip(reading[:-1], reading[1:]):
      if asyl == bsyl:
        score += 5

    if score < best_score:
      best_score = score
      best_reading = reading

  assert(best_reading is not None)

  marked_tokens, marked_syllables = mark_line_with_reading(tokens, dictionary_reading, best_reading)

  return ' '.join(marked_tokens), reading, marked_syllables

class AnnotatedLine:
  def __init__(self, unmarked, marked, syllables, marked_syllables):
    self.unmarked = unmarked
    self.marked = marked
    self.syllables = syllables
    
    self.start_posn, self.end_posn = [], []
    i, posn = 0, 0
    for word in marked_syllables:
      if word == ' ':
        posn += 1
        continue
      if word in punctuation: 
        posn += len(word)
        continue
      self.start_posn.append(posn)
      self.end_posn.append(posn+len(word))
      posn += len(word)
      i += 1

class LineFriend(cmd.Cmd):
  def __init__(self, annotations):
    self.place = 0
    self.line = 0
    self.view = 'meter'
    self.annotations = annotations
    self.window_size = 5

    cmd.Cmd.__init__(self)

  def preloop(self):
    self.postcmd('')

  def postcmd(self, stop, line=''):
    if not stop:
      print '\n' * 3
      for l in xrange(max(0,self.line-self.window_size), self.line):
        if self.view == 'meter':
          print self.annotations[l].marked
        elif self.view == 'emphasize':
          print self.annotations[l].unmarked
        else:
          assert False, 'unknown view'

      if self.view == 'meter':
        print self.annotations[self.line].marked
      elif self.view == 'emphasize':
        a = self.annotations[self.line]
        print (a.marked[:a.start_posn[self.place]].lower() +
               a.marked[a.start_posn[self.place]:a.end_posn[self.place]].upper() +
               a.marked[a.end_posn[self.place]:].lower())
      else:
        assert False, 'unknown view'
      print (' ' * self.annotations[self.line].start_posn[self.place] + 
             '^' * (self.annotations[self.line].end_posn[self.place] - 
                    self.annotations[self.line].start_posn[self.place]))

    for l in xrange(self.line+1,min(len(self.annotations), self.line+self.window_size+1)):
      if self.view == 'meter':
        print self.annotations[l].marked
      elif self.view == 'emphasize':
        print self.annotations[l].unmarked
      else:
        assert False, 'unknown view'

    print

    print '[%s view]' % self.view
    print '''(f)orward  (b)ack  (n)ext line  (p)revious line  (s)tress  (u)nstress
(e)mphasize  (d)eemphasize  (q)uit'''

    return stop

  def do_u(self, line):
    """(u)nstress the current syllable"""
    self.do_unstress(line)

  def do_unstress(self, line):
    """(u)nstress the current syllable"""
    a = self.annotations[self.line]
    a.marked = (
      a.marked[:a.start_posn[self.place]] +
      a.marked[a.start_posn[self.place]:a.end_posn[self.place]].lower() +
      a.marked[a.end_posn[self.place]:])

  def do_s(self, line):
    """(s)tress the current syllable"""
    self.do_stress(line)

  def do_stress(self, line):
    """(s)tress the current syllable"""
    a = self.annotations[self.line]
    a.marked = (
      a.marked[:a.start_posn[self.place]] +
      a.marked[a.start_posn[self.place]:a.end_posn[self.place]].upper() +
      a.marked[a.end_posn[self.place]:])

  def do_e(self, line):
    """(e)mphasize the current syllable"""
    self.do_emphasize(line)

  def do_emphasize(self, line):
    """(e)mphasize the current syllable"""
    self.view = 'emphasize'

  def do_d(self, line):
    """(d)eemphasize the current syllable - go back to showing meter"""
    self.do_deemphasize(line)

  def do_deemphasize(self, line):
    """(d)eemphasize the current syllable - go back to showing meter"""
    self.view = 'meter'

  def do_f(self, line):
    """(f)orward: move to the next syllable"""
    self.do_forward(line)

  def do_b(self, line):
    """(b)ackward: move to the previous syllable"""
    self.do_backward(line)

  def do_forward(self, line):
    """(f)orward: move to the next syllable"""
    self.place = (self.place + 1) % len(self.annotations[self.line].syllables)

  def do_backward(self, line):
    """(b)ackward: move to the previous syllable"""
    self.place = (self.place - 1) % len(self.annotations[self.line].syllables)

  def do_n(self, line):
    """(n)ext: move on to the next line"""
    self.do_next(line)

  def do_next(self, line):
    """(n)ext: move on to the next line"""
    self.line += 1

  def do_p(self, line):
    """(p)revious: move to the previous line"""
    self.do_previous(line)

  def do_previous(self, line):
    """(p)revious: move to the previous line"""
    self.line -= 1

  def do_q(self, line):
    """(q)uit"""
    return True

  def do_quit(self, line):
    """(q)uit"""
    return True

def annotate(text):
  annotations = []
  for line in text:
    marked, syllables, marked_syllables = infer_reading(line)
    print 'Assigning meter:', marked
    annotations.append(AnnotatedLine(line, marked, syllables, marked_syllables))
  return annotations


cmu_dict = dictionaries.read_cmu_dict()
split_dict = dictionaries.read_split_dict()
moby_dict = dictionaries.read_moby_dict()
split_dict = dictionaries.combine_dicts(split_dict, moby_dict)

if len(sys.argv) == 1:
  text = editor.launch_editor(editor='gedit')
  if text.strip() == '':
    print 'No text given'
    sys.exit()
  text = text.split('\n')
  text = [ line for line in text if line.strip() ]
  words = sum([ get_words(line) for line in text ], [])
  # split_dict goes second to take precedence
  split_dict = dictionaries.combine_dicts(
    splitting.get_splits(words, moby_dict, cmu_dict), split_dict)
else:
  if sys.argv[1] in ['hamlet']:
    import mit_shakespeare
    target_excerpt = 'To be, or not to be'
    end_target_excerpt = 'Good my lord'
    parser = mit_shakespeare.MITShakespeareParser(
      target_excerpt=target_excerpt, end_target_excerpt=end_target_excerpt)
    parser.feed('\n'.join(line for line in open('hamlet.html')))
    text = parser.get_text()
  else:
    print 'Unrecognized text:', sys.argv[1]
    sys.exit()

annotations = annotate(text)
LineFriend(annotations).cmdloop()
