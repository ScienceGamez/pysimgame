"""Utility module."""


def recursive_dict_missing_values(dic_from: dict, dic_to: dict):
    """Assign missing values from a dictonary to another.

    Can handle
    """
    for key, value in dic_from.items():
        if key not in dic_to:
            dic_to[key] = value
        elif isinstance(value, dict):
            dic_to[key] = recursive_dict_missing_values(
                dic_from[key], dic_to[key]
            )
        else:
            pass
    return dic_to
