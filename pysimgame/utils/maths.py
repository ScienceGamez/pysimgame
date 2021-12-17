"""Mathematical helper functions."""


def normalize(array):
    """Normalize the array.

    Set all the values betwwen 0 and 1.
    0 corresponds to the min value and 1 the max.
    If the normalization cannot occur, will return the array.
    """
    min_ = min(array)
    max_ = max(array)
    return (
        (array - min_) / (max_ - min_)  # Normalize
        if min_ != max_ else
        array / (max_ if max_ > 0 else 1)  # Avoid divide by 0
    )
