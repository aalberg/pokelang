# Pokelang Project

A silly project to encode English in hypothetical reversible Pokemon languages.

"Translations" are not true translations, but are encodings of one language in
another using intermediate Huffman trees.

## Usage

```shell
pokelang.py <from_language> <to_langauge> <infile> <outfile>
```

## Language specification

Several example languages are specified by JSON files in
[languages/](languages/).

Languages are specified with three required attributes: `name`, `symbols`, and
`tree`, and two optional ones: `drop_extra` and `case_sensitive`.

### `name`

`name` is a string representing the name of the language. This is the name
specified on the command line to translate to or from the language.

### `symbols` and `tree`

`symbols` and `tree` are arrays that encode a Huffman tree using the method
descibed [here](https://stackoverflow.com/a/34603070). `symbols` lists the
discrete symbols that make up the language, and `tree` describes the structure
of the Huffman tree used to encode and decode each symbol.

Each symbol in `symbols` has an several additional constraints:

1. Each symbol must be a string containing only the characters `[a-zA-Z]`. Other
characters are used as delimiters to split words.

2. No two symbols may be concatonated to form a prefix of another symbol.
Single symbols are allowed to be prefixes for other symbols. For example, `pi`
and `pii` are allowed to exist in the same lanauge, but `pi`, `ka` and `pika`
may not coexist, nor may `pi` and `pipi`. This condition is not explicitly
checked, but if a language does not meet the condition there will be encoding
or decoding errors.

### `drop_extra`

`drop_extra` defines how a language behaves when decoding incomplete symbols.
Because different languages use completely different encodings, encoding to
binary with one language and decoding with another may result in an incomplete
symbol at the end of a word.

If `drop_extra` is `true` this incomplete symbol will be dropped. If
`drop_extra` is true the incomplete symbol will be decoded as an existing
symbol that can be prefixed with the incomplete symbol. The selected symbol
will have the shortest encoding of existing symbols with that prefix. Ties will
be broken randomly

`drop_extra` defaults to `false` if not specified.

### `case_sensitive`

Languages may be specified as case sensitive or not case sensitive. If a
language is not case sensitive all symbols in the language and all text to be
translated will be converted to lowercase before translating.

If a language is specified as case sensitive all relevant case variations
symbols with  must be specified in the language specification. See
[here](languages/pikachu.json) language for an example.

`case_sensitive` defaults to `false` if not specified.