import enum
from functools import cache
from string import digits, ascii_letters, ascii_lowercase
identifier_chars = set(digits + ascii_letters + '_$')

class Tokens(enum.Enum):
    comment = 0
    number = 1
    keyword = 2
    identifier = 3
    newline = 4


def join(it, delimiter=None):
    it = iter(it)
    try:
        result = next(it)
    except StopIteration:
        return []
    for el in it:
        if delimiter:
            result += delimiter
        result += el
    return result

def split(s, delimiter):
    j = 0
    for i in range(len(s)):
        if s[i] == delimiter:
            yield s[j:i]
            j = i + 1
    if len(s) and j != len(s):
        yield s[j:len(s)]

def parse_token(src, keywords):
    if src in keywords:
        return (Tokens.keyword, src)
    if all(c in digits for c in src):
        return (Tokens.number, src)
    if src[0] not in digits and all(c in identifier_chars for c in src):
        return (Tokens.identifier, src)
    return None

@cache
def parse_word(src, keywords):
    token = parse_token(src, keywords)
    if token is not None:
        return [token]
    for i in range(len(src) - 1, 0, -1):
        left = parse_token(src[:i], keywords)
        right = parse_word(src[i:], keywords)
        if left is not None and right is not None:
            return [left] + right
    return None
def parse(source, keywords={}):
    keywords = frozenset(keywords)
    parse = lambda source: list(parse_word(source, keywords))
    tokens = []
    #print(source, '-->', list(split(source, '\n')), source.split('\n'))
    for line in source.split('\n'):
        #print('!:', repr(line))
        code, comment = line, []
        if '#' in line:
            code, comment = line.split('#', 1)
            comment = [(Tokens.comment, '#'+comment)]
        code = list(map(parse, code.strip().split(' '))) if code else []
        if any(t is None for t in code):
            return None
        tokens.append(join(code) + comment)
    #print('tokens:', tokens)
    return join(tokens, [(Tokens.newline, '\n')])
