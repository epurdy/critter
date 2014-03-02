(function() {

var snippet = document.getElementById('snippet');
var syllablesTool = document.getElementById('syllables-tool');
var textElement = document.getElementById('text');
var mode = '';

// Fallback client-side syllabification, just splits words into syllables.
function splitOnWordBoundaries(elem) {
  var text = elem.innerText;
  var segments = text.split(/([\w']*)/);
  for (var i = 1; i < segments.length; i += 2) {
    if (segments[i]) {
      segments[i] = '<span class="syllable">' + segments[i] + '</span>';
    }
  }
  var html = segments.join('').replace(/\n/g, '<br>');
  elem.innerHTML = html;
}

// Splits a syllable or merges it with an adjacent syllable.
function splitOrJoinSyllableAt(sel) {
  var range = sel.getRangeAt(0);
  var elem = range.startContainer.parentElement;
  if (elem && elem.classList.contains('syllable')) {
    var text = range.startContainer.textContent;
    if (range.startOffset == 0) {
      var left = elem.previousSibling;
      if (left && left.classList && left.classList.contains('syllable')) {
        elem.parentNode.removeChild(elem);
        left.innerText = left.innerText + text;
      }
    } else if (range.startOffset == text.length) {
      var right = elem.nextSibling;
      if (right && right.classList && right.classList.contains('syllable')) {
        elem.parentNode.removeChild(elem);
        right.innerText = text + right.innerText;
      }
    } else {
      var start = text.substr(0, range.startOffset);
      var end = text.substr(range.startOffset, text.length);
      elem.innerText = end;
      var syl = document.createElement('span');
      syl.className = 'syllable';
      syl.textContent = start;
      elem.parentNode.insertBefore(syl, elem);
    }
  }
}

// Turns syllables mode on or off.
function toggleSyllablesMode() {
  if (mode == 'syllables-mode') {
    mode = '';
    snippet.classList.remove('syllables-mode');
  } else {
    snippet.classList.add('syllables-mode');
    if (!textElement.querySelector('.syllable')) {
      splitOnWordBoundaries(textElement);
    }
    mode = 'syllables-mode';
  }
}

// Called when the text gets clicked.
function clickText(e) {
  if (mode == 'syllables-mode') {
    var sel = window.getSelection();
    if (sel) {
      splitOrJoinSyllableAt(sel);
    }
  }
}

// Called onload to initialize the UI.
function init() {
  syllablesTool.addEventListener('click', toggleSyllablesMode);
  textElement.addEventListener('click', clickText);
}

window.addEventListener('load', init);
})();
