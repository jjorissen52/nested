from contextlib import suppress
from functools import cmp_to_key


"""
This library facilitates the manipulation of nested objects. Particularly objects that are key-accessible, such as lists
and dicts. 
"""


class InvalidKeyPath(BaseException):
    pass


@cmp_to_key
def _integers_matter_more_comparison(a, b):
    """
    This comparison function is used to sort key_lists in the nested_delete function In descending order of the most
    prominent integer. If you delete items from lists with higher indices first, you don't have to worry about
    the indices changing on lower items, since their indices will not change with that deletion.

    (More on key_lists in module description).

    Sorted example:
        l = [['z', 2, 'z'], ['a', 3, 'b']]
        print(sorted(l, key=_integers_matter_more_comparison)
        # [['a', 3, 'b'], ['z', 2, 'z']]
    """
    for i in range(len(a)):
        if isinstance(a[i], int) and isinstance(b[i], int):
            return b[i] - a[i]
        elif isinstance(a[i], int):
            return -1
        elif isinstance(b[i], int):
            return 1
        else:
            with suppress(TypeError):
                return 1 if b > a else -1
    return -1


def nested_get(obj, key_list):
    """
    Get the value of the item at the end of obj[key_list]
    :param obj: any python object, the elements of which are key-accessible
    :param key_list: list of int and string-like objects that can be hashed as keys.
    :return: the value of the item at the end of obj[key_list]
    """
    try:
        if len(key_list) == 1:
            return obj[key_list[0]]
        elif len(key_list) < 1:
            return obj
        else:
            return nested_get(obj[key_list[0]], key_list[1:])
    except:
        raise InvalidKeyPath("Invalid key path.")


def nested_set(obj, key_list, value):
    try:
        if len(key_list) == 1:
            obj[key_list[0]] = value
            return
        elif len(key_list) < 1:
            obj = value
            return
        else:
            nested_set(obj[key_list[0]], key_list[1:], value)

    except:
        raise InvalidKeyPath("Invalid key path.")


def nested_delete(original_obj, delete_key_list):
    delete_key_list = sorted(delete_key_list, key=_integers_matter_more_comparison)
    bracket_notations = []
    for key_path in delete_key_list:
        bracket_notation = "".join(
            [f"""[{key if isinstance(key, int) else '"' + str(key) + '"'}]""" for key in key_path])
        bracket_notations.append(bracket_notation)
    for bracket_notation in bracket_notations:
        with suppress(KeyError, IndexError):
            # this is icky, but I don't know any other way to delete nested objects without knowing
            # the keys ahead of time!
            exec(f"""del original_obj{bracket_notation}""")


def nested_filter(indicator_func, obj):
    _current_path, _path_list = [], []

    def _find_filtered_path(obj, current_path, path_list):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _find_filtered_path(v, [*current_path, k], path_list)
                if indicator_func(k, v):
                    path_list.append([*current_path, k])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _find_filtered_path(v, [*current_path, i], path_list)

    _find_filtered_path(obj, _current_path, _path_list)
    return _path_list


def nested_sibling_filter(indicator_func, sibling_key_func, obj):
    _current_path, _path_list = [], []

    def _find_filtered_path(obj, current_path, path_list):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _find_filtered_path(v, [*current_path, k], path_list)
                if indicator_func(k, v):
                    sibling_key = sibling_key_func(k, v, obj)
                    if sibling_key:
                        path_list.append(([*current_path, k], [*current_path, sibling_key]))
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _find_filtered_path(v, [*current_path, i], path_list)

    _find_filtered_path(obj, _current_path, _path_list)
    return _path_list


def nested_parent_filter(indicator_func, obj):
    _current_path, _path_list = [], []

    def _find_filtered_path(obj, current_path, path_list):
        if isinstance(obj, dict):
            for k, v in obj.items():
                _find_filtered_path(v, [*current_path, k], path_list)
                if indicator_func(k, v):
                    path_list.append([*current_path])
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                _find_filtered_path(v, [*current_path, i], path_list)

    _find_filtered_path(obj, _current_path, _path_list)
    return _path_list


def get_all_paths(obj):
    return nested_parent_filter(lambda x, y: True, obj)
