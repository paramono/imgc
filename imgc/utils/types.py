from argparse import ArgumentTypeError
from imgc.image import ImageSize

def quality_type(x):
    '''
    argparse quality validator for JPEGs
    accepts values from 1 to 100
    '''
    try:
        x = int(x)
        if x < 1:
            raise ArgumentTypeError("Minimum JPEG quality is 1")
        if x > 100:
            raise ArgumentTypeError("Maximum JPEG quality is 100")
    except ValueError as exc:  # when conversion to int fails
        raise ArgumentTypeError from exc
    return x


def size_type(x):
    '''
    argparse size validator for images
    attempts to imitate imagemagick patterns
    (see Size.PATTERNS for additional info)

    '''

    for method_name, pattern in ImageSize.PATTERNS:
        caught = pattern.match(x)
        if caught:
            break
    else:
        raise ArgumentTypeError("Invalid size pattern")

    print(x)
    return x
