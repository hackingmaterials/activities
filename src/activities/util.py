from typing import Hashable, Dict, Any, Tuple, List, Union, Iterable


def find_key_value(
    d: Union[Dict[Hashable, Any], List[Any]], key: Hashable, value: Hashable
) -> Tuple[List[Any], ...]:
    """
    Find the route to key: value pairs in a dictionary.

    This function works on nested dictionaries, lists, and tuples.

    Parameters:
    -----------
    d
        A dict or list of dicts.
    key
        A dictionary key.
    value
        A value.

    Returns:
    --------
    A tuple of routes to where the matches were found.

    Examples:
    ---------

    >>> data = {
    ...    "a": [0, {"b": 1, "x": 3}],
    ...    "c": {"d": {"x": 3}}
    ... }
    ... find_key_value(data, "x", 3)
    (('a', 1), ('c', 'd'))
    """
    found_items = set()

    def _lookup(obj, path=None):
        if path is None:
            path = ()

        if isinstance(obj, dict):
            if key in obj and obj[key] == value:
                found_items.add(path)

            for k, v in obj.items():
                _lookup(v, path + (k,))

        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                _lookup(v, path + (i,))

    _lookup(d)
    return tuple(found_items)
