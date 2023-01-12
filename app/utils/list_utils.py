def list_to_dict(src_list):
    if not src_list:
        return {}
    return dict(list(zip(src_list[0::2], src_list[1::2])))


def count_key(key, dict_list):
    keys_list = []
    for item in dict_list:
        keys_list += item.keys()
    return keys_list.count(key)
