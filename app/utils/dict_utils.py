from typing import Any


def safe_get(data_dict: dict, key: str, default: Any = None):
    """Safely extracts a key from dict. If key is not found or the input is not dict then return None.

    Args:
        data_dict (dict): A dict from which key is to be extracted.
        key (str): The key which needs to be extracted.
        default (Any): The default value that needs to be returned if the key is not found
    Returns:
        The value in the passed key.

    Raises:
        N/A

    Examples:
        >>> safe_get({"key1":"val1","key2":{"key3":"val3"}}, "key1")
        "val1"

    """
    if not isinstance(data_dict, dict):
        return None
    return data_dict.get(key, default)


# b=None
# a = {"k1": 1, "k2":{"k3": "jabba"}}
# print(safe_get(a,"k1"))
# print(safe_get(b,"k1"))
# print(safe_get(a,"k2"))
# print(safe_get(a,"k4"))
