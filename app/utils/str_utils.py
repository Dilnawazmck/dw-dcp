def safe_strip(key):
    if not isinstance(key, str):
        return key
    return key.strip()


def safe_concat(*args):
    concat_str = ""
    for string in args:
        concat_str += str(string) if string else ""
    return concat_str
