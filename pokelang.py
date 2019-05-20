import sys
import re

kAllRetext = "[a-zA-Z]+"

kEnglishCode = {
  "E": "011",
  "T": "000",
  "A": "1110",
  "O": "1101",
  "I": "1011",
  "H": "1010",
  "N": "1001",
  "S": "1000",
  "R": "0101",
  "D": "11111",
  "L": "11110",
  "C": "01001",
  "U": "01000",
  "M": "00111",
  "W": "00110",
  "F": "00101",
  "G": "110011",
  "Y": "110010",
  "P": "110001",
  "B": "110000",
  "V": "001000",
  "K": "0010011",
  "J": "001001011",
  "X": "001001010",
  "Q": "001001001",
  "Z": "001001000"
}

kPikaCode = {
  "pi": "00",
  "pii": "01",
  "ka": "10",
  "chu": "11"
}

def translateWord(word, from_map, to_map):
  return decode(encode(word.upper(), from_map), to_map, False)

def encode(word, map):
  code_pieces = []
  for i in range(len(word)):
    code_pieces += [map[word[i]]]
  return "".join(code_pieces)

def decode(word, map, drop_extra = False):
  return word
  #inv_map = {v: k for k, v in my_map.items()}


def translate(file_contents):
  index = 0
  words = []
  for match in re.finditer(kAllRetext, file_contents):
    span = match.span()
    words += [file_contents[index:(span[0])], \
              translateWord(match.group(), kEnglishCode, kPikaCode)]
    index = span[1]
  words += [file_contents[index:]]
  final = "".join(words)
  print(final)
  return final

# Usage: python pokelang.py <infile> <outfile>
if __name__ == "__main__":
  if len(sys.argv) != 3:
    print("Wrong number of argv")
    exit(1)
  else:
    with open(sys.argv[1]) as f:
      final = translate(f.read())
      with open(sys.argv[2], "w+") as f2:
        f2.write(final)