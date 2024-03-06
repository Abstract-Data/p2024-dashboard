

def clear_blank_strings(cls, values):
    """
    Clear out all blank strings or ones that contain 'null' from records.
    :param cls:
    :param values:
    :return:
    """
    for k, v in values.items():
        if v in ["", '"', "null"]:
            values[k] = None
        if k in ["", '"', "null"]:
            values[k] = values[k].replace(k, None)
    return values