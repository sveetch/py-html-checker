
def reduce_unique(items):
    """
    Reduce given list to a list of unique values and respecting original order
    base on first value occurences.

    Arguments:
        items (list): List of element to reduce.

    Returns:
        list: List of unique values.
    """
    used = set()
    return [x for x in items if x not in used and (used.add(x) or True)]


def merge_compute(left, right):
    """
    Merge two dictionnaries but computing integer values instead of overriding.

    Left override every right values except when both left and right value are
    integers then right value will be incremented by left value.

    Arguments:
        left (dict): The dict to merge into right.
        right (dict): The merge in the left dict.

    Returns:
        dict: Merged dict from left to right.
    """
    for k, v in left.items():
        # Only compute item if both left and right values are integers, else
        # left override right value
        if k in right and type(v) is int and type(right[k]) is int:
            right[k] += v
        else:
            right[k] = v

    return right
