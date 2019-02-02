import datetime


def escape(input):
    """
    Escape input
    :param input:
    :return: escaped value
    """

    if input is None:
        return input

    if type(input) in (tuple, list):
        return [escape(i) for i in input]

    if type(input) is dict:
        return {escape(k): escape(v) for k, v in input.items()}

    if type(input) in (int, float, bool):
        return input

    if type(input) is str:
        return escape_str(input)

    if type(input) is datetime.datetime:
        return input

    raise AttributeError("Unknown input type type:%s; value:%s" % (type(input), input))


def escape_str(input):
    """
    Escape input
    :param input:
    :return: escaped value
    """

    return input.replace("<", "").replace(">", "")
