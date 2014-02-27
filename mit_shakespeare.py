from HTMLParser import HTMLParser

class MITShakespeareParser(HTMLParser):
  def __init__(self, target_excerpt, end_target_excerpt):
    HTMLParser.__init__(self)
    self.started = False
    self.inquote = False
    self.num_lines_seen = 0

    self.target_excerpt_active = False
    self.target_excerpt = target_excerpt
    self.end_target_excerpt = end_target_excerpt

    self.text_lines = []

    self.max_lines = 73

  def handle_starttag(self, tag, attrs):
    tag = tag.lower()
    if tag == 'h3':
      self.started = True

    if tag == 'blockquote':
      self.inquote = True

    if tag == 'i': # stage directions
      self.inquote = False

    if not self.started:
      return

    return

    print "Start tag:", tag
    for attr in attrs:
      print "     attr:", attr

  def handle_endtag(self, tag):
    tag = tag.lower()
    if not self.started:
      return

    if tag == 'blockquote':
      self.inquote = False

    return

    print "End tag  :", tag

  def handle_data(self, data):
    if not self.started: 
      return
    if not data.strip(): 
      return
    if not self.inquote:
      return

    if not self.target_excerpt_active:
      if self.target_excerpt in data:
        self.target_excerpt_active = True
      else:
        return
    else:
      if self.end_target_excerpt in data:
        self.target_excerpt_active = False
        return
    

    if self.num_lines_seen >= self.max_lines:
      return

    self.num_lines_seen += 1

#    print "Data     :", data
    self.text_lines.append(data)

  def get_text(self):
    return self.text_lines
