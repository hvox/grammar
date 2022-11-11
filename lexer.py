import re
from string import ascii_letters, digits, whitespace
from typing import Callable


def get_very_simple_lexer(punctuation=set(), variable_characters=None):
    if variable_characters is None:
        variable_characters = ascii_letters + digits + " "

    def scan(source: str, i: int = 0):
        while i < len(source):
            char = source[i]
            if char in punctuation:
                i += 1
                yield (char, char)
            elif char in whitespace:
                i += 1
            elif char in "'\"":
                j = i + 1
                while j < len(source) and source[j] != char:
                    j += 1
                yield ("terminal", source[i+1:j])
                i = j + 1
            elif char in digits:
                j = i + 1
                while j < len(source) and source[j] in digits:
                    j += 1
                yield ("number", int(source[i:j]))
                i = j
            elif char in variable_characters:
                j = i + 1
                while j < len(source) and source[j] in variable_characters:
                    j += 1
                yield ("identifier", source[i:j].strip())
                i = j
            else:
                raise ValueError(f"Unexpected character: {repr(char)}")
        yield (None, None)
    return scan


def construct_lexer(patterns: dict[str | re.Pattern, None | Callable]):
    recognizers = [
        (re.compile(re.escape(pat)) if isinstance(pat, str) else pat, f)
        for pat, f in patterns.items()
    ]

    def scan(source: str, i: int = 0):
        while i < len(source):
            for regex, postprocessing in recognizers:
                if match := regex.match(source, i):
                    if postprocessing is not None:
                        yield postprocessing(match.span(), match.group())
                    i = match.end()
                    break
            else:
                raise ValueError(f"Unexpected character: {repr(source[i])}")
    return scan
