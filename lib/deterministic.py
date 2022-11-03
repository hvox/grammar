from typing import TypeVar, Iterable, Iterator

T = TypeVar("T")


class DeterministicSet(Iterable[T]):
    def __init__(self, elements: Iterable[T] = ()):
        self.elements = dict.fromkeys(elements)

    def __iter__(self) -> Iterator[T]:
        yield from self.elements

    def __sub__(self, other: "DeterministicSet[T] | set[T]"):
        return DeterministicSet(x for x in self.elements if x not in other)

    def __or__(self, other: "DeterministicSet[T] | set[T]"):
        return DeterministicSet(self.elements | dict.fromkeys(other))

    def __and__(self, other: "DeterministicSet[T] | set[T]"):
        return DeterministicSet(x for x in self.elements if x in other)

    def __contains__(self, x):
        return x in self.elements

    def __repr__(self):
        return "{"  + ", ".join(map(repr, self.elements)) + "}"

    def __len__(self):
        return len(self.elements)

    def __eq__(self, other: "DeterministicSet[T] | set[T]"):
        return len(self) == len(other) and set(self) == set(other)

    def add(self, x: T):
        self.elements[x] = None
