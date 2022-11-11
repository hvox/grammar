def add_to_set(collection: set, element: str):
    while element in collection:
        element += "'"
    collection.add(element)
    return element
