# bins - idea for package name if I ever put this thing on pypy
from collections.abc import Hashable, MutableSequence, MutableSet, Sequence, Set
from typing import Any, Iterable, Iterator, Self, TypeVar, overload

T = TypeVar("T")


class OrderedSet(Set[T]):
    __slots__ = ("elements",)

    def __init__(self, iterable: Iterable[T] = ()):
        self.elements: dict[T, None] = dict.fromkeys(iterable)

    def __contains__(self, element: Any) -> bool:
        return element in self.elements

    def __iter__(self) -> Iterator[T]:
        return iter(self.elements)

    def __len__(self) -> int:
        return len(self.elements)

    def __repr__(self) -> str:
        return f"OrderedSet({list(self.elements)})"


class MutableOrderedSet(OrderedSet[T], MutableSet[T]):
    def add(self, element: T) -> None:
        self.elements[element] = None

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        self.elements.pop(element, None)

    def remove(self, element: T) -> None:
        del self.elements[element]


class GrowableOrderedSet(OrderedSet[T]):
    __slots__ = ("values", "indexes")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def add(self, element: T) -> None:
        if element not in self.indexes:
            self.values.append(element)
            self.indexes[element] = len(self.indexes)

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"OrderedSet({self.values})"


class FrozenOrderedSet(OrderedSet[T], Hashable):
    def __hash__(self) -> int:
        return hash(tuple(self.elements))


class IndexedSet(Sequence[T], Set[T]):
    __slots__ = ("indexes", "values")

    def __init__(self, iterable: Iterable[T] = ()):
        elements = dict.fromkeys(iterable)
        self.values: list[T] = list(elements)
        self.indexes: dict[T, int] = {v: i for i, v in enumerate(elements)}

    def __contains__(self, element: Any) -> bool:
        return element in self.indexes

    def __iter__(self) -> Iterator[T]:
        return iter(self.values)

    def __len__(self) -> int:
        return len(self.values)

    def __repr__(self) -> str:
        return f"IndexedSet({self.values})"

    @overload
    def __getitem__(self, i: int) -> T:
        ...

    @overload
    def __getitem__(self, i: slice) -> Self:
        ...

    def __getitem__(self, i: int | slice) -> T | Self:
        if isinstance(i, int):
            return self.values[i]
        start = i.start if i.start is not None else 0
        stop = i.stop if i.stop is not None else len(self.values) - 1
        step = i.step if i.step is not None else 1
        return IndexedSet(self.values[i] for i in range(start, stop, step))


class FrozenIndexedSet(IndexedSet[T], Hashable):
    def __hash__(self) -> int:
        return hash(tuple(self.values))


class MutableIndexedSet(IndexedSet[T], MutableSequence[T], MutableSet[T]):
    def __delitem__(self, i: int | slice) -> None:
        if isinstance(i, int):
            return self.remove(self.values[i])
        start = i.start if i.start is not None else 0
        stop = i.stop if i.stop is not None else len(self.values) - 1
        step = i.step if i.step is not None else 1
        for i in range(start, stop, step) if step < 0 else reversed(range(start, stop, step)):
            self.remove(self.values[i])

    @overload
    def __setitem__(self, i: int, value: T) -> None:
        ...

    @overload
    def __setitem__(self, i: slice, iterable: Iterable[T]) -> None:
        ...

    def __setitem__(self, i: int | slice, vals: Any) -> None:
        match i:
            case int(i):
                new_value, old_value = vals, self.values[i]
                if new_value != old_value:
                    if new_value in self.indexes:
                        raise ValueError(f"{new_value!r} is already in the set")
                    del self.indexes[old_value]
                    self.values[i] = new_value
                    self.indexes[new_value] = i
            case i:
                start = i.start if i.start is not None else 0
                stop = i.stop if i.stop is not None else len(self.values) - 1
                step = i.step if i.step is not None else 1
                slice_size, new_values = (stop - start) // step, list(vals)
                if slice_size != len(new_values):
                    raise ValueError(
                        f"attempt to assign sequence of size {len(new_values)} "
                        f"to extended slice of size {slice_size}"
                    )
                for i in range(start, stop, step):
                    del self.indexes[self.values[i]]
                for i, value in zip(range(start, stop, step), new_values):
                    if value in self.indexes:
                        raise ValueError(f"{value!r} is already in the set")
                    self.values[i] = value
                    self.indexes[value] = i

    def insert(self, i: int, element: T) -> None:
        if i == len(self.values):
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            return self.add(element)
        old_value = self.values[i]
        if element != old_value:
            if element in self.indexes:
                raise ValueError(f"{element!r} is already in the set")
            self.indexes[old_value] = len(self.values)
            self.values.append(old_value)
            self.indexes[element] = i
            self.values[i] = element

    def add(self, element: T) -> None:
        if element not in self.indexes:
            self.values.append(element)
            self.indexes[element] = len(self.indexes)

    def push(self, element: T) -> int:
        i = self.indexes.get(element, len(self.indexes))
        if i == len(self.values):
            self.values.append(element)
            self.indexes[element] = i
        return i

    def update(self, elements: Iterable[T]) -> None:
        for x in elements:
            self.add(x)

    def discard(self, element: T) -> None:
        if element in self.indexes:
            self.remove(element)

    def remove(self, element: T) -> None:
        i = self.indexes.pop(element)
        if i == len(self.indexes):
            self.values.pop()
        else:
            self.values[i] = self.values.pop()
            self.indexes[self.values[i]] = i

    def freeze(self) -> FrozenIndexedSet[T]:
        frozen_set: FrozenIndexedSet[T] = FrozenIndexedSet()
        frozen_set.values, frozen_set.indexes = self.values, self.indexes
        self.values, self.indexes = [], {}
        return frozen_set
