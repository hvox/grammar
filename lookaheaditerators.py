class LookAheadIterator:
    def __init__(self, it):
        self.iterator = iter(it)
        self.next = None
        self.goto_next()

    def goto_next(self):
        current = self.next
        try:
            self.next = (next(self.iterator),)
        except StopIteration:
            self.next = None
        return current

    def get_next(self):
        elem = self.next
        return None if elem is None else elem[0]

    def __next__(self):
        elem = self.goto_next()
        return None if elem is None else elem[0]

    def __iter__(self):
        while True:
            current = self.goto_next()
            if current is None:
                return
            yield current[0]
