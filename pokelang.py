import sys
import re
import json
import os
from collections import deque

kAllRetext = "[a-zA-Z]+"
kDefaultLangaugeDir = "./languages"
kLanguageMap = {}

class HuffmanTree:
  # TODO: Support for degree != 2
  kDegree = 2
  def __init__(self):
    self.name = None
    self.drop_extra = False
    self.case_sensitive = False
    self.root = None
    self.leaves = None
    self.symbol_tree = None

  def load(self, data):
    if not HuffmanTree.validateLangauge(data):
      return (False, "Failed initial validation")

    # Reconstruct a Huffman tree from the JSON data. Coding is described here:
    # https://stackoverflow.com/a/34603070
    self.name = data["name"]
    if "drop_extra" in data:
      self.drop_extra = data["drop_extra"]
    if "case_sensitive" in data:
      self.case_sensitive = data["case_sensitive"]
    self.leaves = {}
    self.root = HuffmanNode(None, None)
    active_nodes = [self.root]
    symbol_index = 0
    for tree_bit in data["tree"]:
      cur = active_nodes.pop()
      if tree_bit == 0:
        for i in range(HuffmanTree.kDegree):
          cur.children.append(HuffmanNode(cur, i))
        active_nodes.extend(reversed(cur.children))
      elif tree_bit == 1:
        symbol = data["symbols"][symbol_index]
        if not self.case_sensitive:
          symbol = symbol.lower()
        cur.symbol = symbol
        self.leaves[cur.symbol] = cur
        symbol_index += 1
        if symbol_index > len(data["symbols"]):
          return (False, "Length error: {}, {}"
              .format(symbol_index, len(data["symbols"])))
      else:
        return (False, "Encoding error: {}".format(tree_bit))

    # Generate codes for each leaf and add each symbol to the prefix tree.
    # TODO: Track the current while building the tree to avoid the tracing up
    # the tree here.
    self.symbol_tree = PrefixTree()
    for symbol, node in self.leaves.items():
      cur = node
      bits = []
      while cur.bit != None:
        bits.append(cur.bit)
        cur = cur.parent
      node.code = "".join(str(b) for b in reversed(bits))
      self.symbol_tree.insert(symbol)
    return (True, None)

  def validateLangauge(data):
    return "name" in data and "symbols" in data and "tree" in data

  def encodeWord(self, word):
    if not self.case_sensitive:
      word = word.lower()
    (status, result) = self.parseIntoSymbols(word)
    if not status:
      return (status, "\"{}\" cannot be encoded in language {}: {}" \
              .format(word, self.name, result))
    return (True, self.translateSymbols(result))

  def parseIntoSymbols(self, word):
    i = 0
    symbol_list = []
    cur_prefixes = self.symbol_tree.getPrefixes(word[i:])
    while i < len(word):
      found_prefix = False
      for prefix in cur_prefixes:
        new_i = i + len(prefix)
        if new_i > len(word):
          continue
        elif new_i == len(word):
          i = new_i
          symbol_list.append(prefix)
          found_prefix = True
          break
        new_prefixes = self.symbol_tree.getPrefixes(word[new_i:])
        # At most one prefix can result in a parsable remaining word.
        if new_prefixes != None:
          i = new_i
          cur_prefixes = new_prefixes
          symbol_list.append(prefix)
          found_prefix = True
          break;

      if not found_prefix:
        return (False, "Could not find valid prefix for at index {} for {}" \
                .format(i, word[i:]))
    return (True, symbol_list)

  def translateSymbols(self, symbol_list):
    codes = []
    for symbol in symbol_list:
      codes.append(self.leaves[symbol].code)
    return "".join(codes)

  def decodeWord(self, word):
    symbols = []
    cur = self.root
    for i in range(len(word)):
      c = -1
      if word[i] == "0":
        c = 0
      elif word[i] == "1":
        c = 1
      else:
        return (False, "Encoding error: {} at index: {}".format(word[i], i))

      cur = cur.children[c]
      if cur.symbol != None:
        symbols.append(cur.symbol)
        cur = self.root
    if not self.drop_extra and cur != self.root:
      # TODO: Do this bfs once after building the tree and store partial symbol
      # decodings in each node, instead of doing it at the end of each word.
      horizon = deque([cur])
      done = False
      while not done:
        h = horizon.popleft()
        for c in h.children:
          if c.symbol != None:
            symbols.append(c.symbol)
            done = True
            break
          horizon.append(c)
    return (True, "".join(symbols))

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    return "{}\n{}".format(self.name, self.root.__repr__())

class HuffmanNode:
  def __init__(self, parent, bit):
    self.symbol = None
    self.code = None
    self.parent = parent
    self.bit = bit
    self.children = []

  def prettyPrint(self, depth = 0):
    return " " * depth + str(self.symbol) + "\n" + \
           "".join(c.prettyPrint(depth + 1) for c in self.children)

  def __str__(self):
    return str(self.symbol)

  def __repr__(self):
    return self.prettyPrint(0)

class PrefixTree:
  def __init__(self):
    self.root = PrefixNode()

  def insert(self, word):
    cur = self.root
    for c in word:
      if c in cur.children:
        cur = cur.children[c]
      else:
        next = PrefixNode()
        cur.children[c] = next
        cur = next
    cur.word = word

  def getPrefixes(self, word):
    cur = self.root
    prefixes = []
    for c in word:
      if c not in cur.children:
        break
      cur = cur.children[c]
      if cur.word != None:
        prefixes.append(cur.word)
    if len(prefixes) == 0:
      return None
    return prefixes

  def __str__(self):
    return self.__repr__()

  def __repr__(self):
    return self.root.__repr__()

class PrefixNode:
  def __init__(self):
    self.word = None
    self.children = {}

  def prettyPrint(self, depth = 0):
    padding = " " * depth
    parts = [str(self.word), "\n"]
    for s, c in self.children.items():
      c_padding, c_str = c.prettyPrint(depth + 1)
      parts.extend([c_padding, s, ": ", c_str])
    return padding, "".join(parts)

  def __str__(self):
    return str(self.symbol)

  def __repr__(self):
    return "".join(self.prettyPrint(0))

def loadLanguages(directory = kDefaultLangaugeDir):
  if directory[-1] != "/":
    directory += "/"
  (dirpath, dirnames, filenames) = next(os.walk(directory))
  for f in filenames:
    loadLanguage(dirpath, f)

def loadLanguage(directory, file):
  with open(directory + file) as f:
    tree = HuffmanTree()
    (status, result) = tree.load(json.load(f))
    if status:
      kLanguageMap[tree.name] = tree
    else:
      print("Error parsing language from file {}: {}".format(file, result))

def translate(text, from_langauge, to_langauge):
  kErrorTemplate = "\"{}\" is not a valid langauge"
  for langauge in [from_langauge, to_langauge]:
    if langauge not in kLanguageMap:
      return (False, kErrorTemplate.format(langauge))
  return translateLangauges(text, kLanguageMap[from_langauge], \
                            kLanguageMap[to_langauge])

def translateLangauges(text, from_tree, to_tree):
  index = 0
  words = []
  for match in re.finditer(kAllRetext, text):
    span = match.span()
    (status, result) = translateWord(match.group(), from_tree, to_tree)
    if not status:
      return (status, result)
    words.extend([text[index:(span[0])], result])
    index = span[1]
  words.append(text[index:])
  final = "".join(words)
  return (True, final)

def translateWord(word, from_tree, to_tree):
  kErrorTemplate = "\"{}\" could not be translated from {} to {}:"
  (status, result) = from_tree.encodeWord(word)
  encoded = result
  if not status:
    return (status, \
            kErrorTemplate.format(word, from_tree.name, to_tree.name, result))
  (status, result) = to_tree.decodeWord(result)
  if not status:
    return (status, \
            kErrorTemplate.format(word, from_tree.name, to_tree.name, result))
  # print("{}: {}: {}".format(word, encoded, result))
  return (status, result)

def main():
  if len(sys.argv) != 5:
    print("Wrong number of argv")
    exit(1)
  else:
    loadLanguages()
    with open(sys.argv[3]) as f:
      (status, result) = translate(f.read(), sys.argv[1], sys.argv[2])
      if status:
        print(result)
        with open(sys.argv[4], "w+") as f2:
          f2.write(result)
      else:
        print("Error: {}".format(result))

# Usage: python pokelang.py <from_language> <to_langauge> <infile> <outfile>
if __name__ == "__main__":
  main()
