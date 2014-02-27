#!/usr/bin/env python

import os
import subprocess
import tempfile

DEFAULT_EDITOR = "vi"

def get_editor():
  editor = os.environ.get("VISUAL")
  if not editor:
    editor = os.environ.get("EDITOR")
  if not editor:
    editor = DEFAULT_EDITOR

  return editor


def launch_editor(editor=None, path=None):
  """Launch an editor, with an optional pre-existing path. Return a string with
  what the user saved in the file."""
  if editor == None:
    editor = get_editor()
  remove_path = False
  if path == None:
    handle, path = tempfile.mkstemp()
    remove_path = True

  p = subprocess.Popen([editor, path])
  p.wait()
  buf = open(path).read()

  if remove_path:
    os.remove(path)

  return buf
