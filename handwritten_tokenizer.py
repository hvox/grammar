import enum
from string import digits, ascii_letters, ascii_lowercase

identifier_chars = set(digits + ascii_letters + "_$")


class Tokens(enum.Enum):
    comment = enum.auto()
    number = enum.auto()
    keyword = enum.auto()
    identifier = enum.auto()
    newline = enum.auto()


def parse_number(source, keywords={}, offset=0):
    j = offset
    while j < len(source) and source[j] in digits:
        j += 1
    if j > offset:
        return (Tokens.number, source[offset:j]), j
    return None, offset


def parse_word(source, keywords={}, offset=0):
    j = offset
    if j >= len(source) or source[j] in digits:
        return None, offset
    while j < len(source) and source[j] in identifier_chars:
        j += 1
    if j > offset:
        return (Tokens.identifier, source[offset:j]), j
    return None, offset


def parse_keyword(source, keywords={}, offset=0):
    for n, keyword in reversed(sorted((len(kw), kw) for kw in keywords)):
        if offset + n > len(source) or source[offset : offset + n] != keyword:
            continue
        return (Tokens.keyword, keyword), offset + n
    return None, offset


def parse_comment(source, keywords={}, offset=0):
    j = offset
    if j >= len(source) or source[j] != "#":
        return None, offset
    while j < len(source) and source[j] != "\n":
        j += 1
    return (Tokens.comment, source[offset:j]), j


def parse_token(source, keywords={}, offset=0):
    best_offset, result = 0, None
    for parser in (parse_keyword, parse_number, parse_word, parse_comment):
        token, new_offset = parser(source, keywords, offset)
        if new_offset > best_offset:
            best_offset, result = new_offset, token
    return result, best_offset


def parse(source, keywords={}, offset=0):
    tokens = []
    while offset < len(source):
        if source[offset] in " \n":
            if source[offset] == "\n":
                tokens.append((Tokens.newline, "\n"))
            offset += 1
        else:
            token, offset = parse_token(source, keywords, offset)
            if not token:
                return None
            tokens.append(token)
    return tokens


def ascii_lowercase_words():
    yield from ascii_lowercase
    for word in ascii_lowercase_words():
        for letter in ascii_lowercase:
            yield word + letter


def skip(it, prohibited_words):
    for elem in it:
        if elem not in prohibited_words:
            yield elem


def ordered_set(it):
    result, visited = [], set()
    for value in it:
        if value not in visited:
            result.append(value)
            visited.add(value)
    return result


def minificate(tokens, keywords):
    ignored_tokens = {Tokens.comment, Tokens.newline}
    tokens = [t for t in tokens if t[0] not in ignored_tokens]
    identifiers = ordered_set(n for t, n in tokens if t == Tokens.identifier)
    new_names = dict(zip(identifiers, skip(ascii_lowercase_words(), keywords)))
    f = lambda t: (t[0], new_names[t[1]]) if t[0] == Tokens.identifier else t
    return list(map(f, tokens))


def ff(tokens):
    if tokens is None:
        return "NONE"
    return ":".join(repr(t[1]) for t in tokens)


def tokens_to_str(tokens, keywords):
    result = [(Tokens.newline, "\n")]
    for t in tokens:
        if parse(result[-1][1] + t[1], keywords) != [result[-1], t]:
            result.append((None, " "))
        result.append(t)
    return "".join(t[1] for t in result)
