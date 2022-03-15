import enum

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
