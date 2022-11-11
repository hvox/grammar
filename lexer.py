from string import whitespace, digits, ascii_letters


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
                yield ("identifier", source[i:j])
                i = j
            else:
                raise ValueError(f"Unexpected character: {repr(char)}")
        yield (None, None)
    return scan
