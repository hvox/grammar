class LookAheadIterator:
    def __init__(self, it):
        self.iterator = iter(it)
        self.finished = False
        self.next = None
        self.goto_next()

    def goto_next(self):
        current = self.next
        try:
            self.next = next(self.iterator)
        except StopIteration:
            self.next = None
            self.finished = True
        return current

    def get_next(self):
        elem = self.next
        return elem

    def __next__(self):
        elem = self.goto_next()
        return elem

    def __iter__(self):
        while not self.finished:
            current = self.goto_next()
            yield current
