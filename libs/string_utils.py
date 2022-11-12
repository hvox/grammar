def split_str(string: str, sep: str, maxsplit: int = -1) -> tuple[str, ...]:
    result = []
    # for is_space, word in groupby(string.split(sep, maxsplit), lambda w: w == ""):
    for word in string.split(sep, maxsplit):
        if word == "" and result and isinstance(result[-1], int):
            word = [result.pop() + 1]
        result.append(word or 0)
    return [x if isinstance(x, str) else sep * x for x in result]
