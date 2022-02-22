class LookAheadIterator:
    def __init__(self, it):
        self.iterator = iter(it)
        self.finished = False
        self.next = None
        next(self)

    def __next__(self):
        current = self.next
        try:
            self.next = next(self.iterator)
        except StopIteration:
            self.next = None
            self.finished = True
        return current

    def __iter__(self):
        while not self.finished:
            current = next(self)
            yield current
