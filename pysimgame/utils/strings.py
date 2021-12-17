def beautify_parameter_name(s: str) -> str:
    """Make a parameter name look better.

    Good for parameter names that have words separated by _ .

    1. change _ by spaces.
    2. First letter is uppercased.
    """
    new_s = " ".join(s.split("_"))
    return new_s.capitalize()
