class LookAheadIterator:
    def __init__(self, it, end=None):
        self.iterator = iter(it)
        self.finished = False
        self.next = None
        self.none = end
        next(self)

    def __next__(self):
        current = self.next
        try:
            self.next = next(self.iterator)
        except StopIteration:
            self.next = self.none
            self.finished = True
        return current

    def __iter__(self):
        while not self.finished:
            current = next(self)
            yield current

    def __repr__(self):
        return f"<lookahead_iterator(next={self.next}) at {hex(id(self))}>"
