def iterable(obj, delimiter=",", last_delimiter="and", repr_=False) -> str:
    """
    Returns a formatted string representation of an array
    """
    if repr_:
        sorted_ = sorted(repr(element) for element in obj)
    else:
        sorted_ = sorted(f"'{element}'" for element in obj)

    if len(sorted_) > 1:
        sorted_[-1] = f'{last_delimiter} {sorted_[-1]}'

    return f"{delimiter} ".join(sorted_)
