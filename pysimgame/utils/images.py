from pathlib import Path
from typing import Tuple
from skimage.transform import resize
from skimage.io import imread, imsave


def resize_image(source: Path, dest: Path, dimensions: Tuple[int, int]):
    """Resize the source image and save it in dest."""
    x, y = dimensions
    # Size is inverted
    img = imread(source)
    res = resize(img, (int(y), int(x)))

    imsave(dest, res)
