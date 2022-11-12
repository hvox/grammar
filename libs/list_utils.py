def push_if_not_in(xs: list, x):
    try:
        return xs.index(x)
    except ValueError:
        xs.append(x)
        return len(xs) - 1
