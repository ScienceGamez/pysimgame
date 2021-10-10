from skimage.transform import resize
from skimage.io import imread, imsave


def resize_image(img_file, x, y):
    # Size is inverted
    img = imread(img_file)
    res = resize(img, (int(y), int(x)))

    imsave("{}_{}x{}.jpg".format(img_file, x, y, ), res)
