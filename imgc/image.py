import re
from .utils import tofrac


class ImageSize():
    '''
    relative size patterns:
    70%x80%
    70%
    70%x
    x80%

    absolute size patterns:
    800x600
    800
    800x
    x600

    TODO:
    ! < > ^ flags
    '''

    PATTERN_RELATIVE = re.compile(
        "^((?P<width>\d+)%)?(x((?P<height>\d+)%)?)?$")
    PATTERN_ABSOLUTE = re.compile(
        "^(?P<width>\d+)?(x(?P<height>\d+)?)?$")
    PATTERNS = (
        ("_parse_absolute", PATTERN_ABSOLUTE),
        ("_parse_relative", PATTERN_RELATIVE),
    )

    @classmethod
    def _parse_absolute(cls, new_size, image=None, **kwargs):
        '''
        takes integer tuples, each integer is a number of pixels
        '''
        return cls._parse_tuple(new_size, image, **kwargs)

    @classmethod
    def _parse_relative(cls, new_size, image=None, **kwargs):
        '''
        takes integer tuples,
        each integer is a percentage of original image size
        '''

        width, height = new_size
        if not width and not height:
            raise ValueError(
                'Relative size requires at least one dimension defined'
            )
        if not width:
            width = height  # same percentage
        if not height:
            height = width  # same percentage

        width = int(tofrac(width) * image.size[0])
        height = int(tofrac(height) * image.size[1])

        new_size = (width, height,)
        return cls._parse_tuple(new_size, image, **kwargs)

    @classmethod
    def _parse_tuple(cls, new_size, image=None, **kwargs):
        width, height = new_size
        if image:
            if not width and not height:
                raise ValueError(
                    'new_size requires at least one dimension defined')

            aratio = image.size[0]/image.size[1]
            if not width:
                width = int(height * aratio)  # wnew = hnew * (w / h)
            if not height:
                height = int(width / aratio)  # hnew = wnew / (w / h)
        else:
            if not width or not height:
                raise ValueError(
                    'new_size must be a 2-tuple since '
                    'image argument is not supplied'
                )
        return (width, height)

    @classmethod
    def _parse_string(cls, new_size, image=None, **kwargs):
        for method_name, pattern in cls.PATTERNS:
            match = pattern.match(new_size)
            if match:
                # These values aren't necessarily pixels!
                # These might be percentages!
                width_str, height_str = \
                    match.group('width'), match.group('height')

                # converting to int only if string is found
                width = int(width_str) if width_str else None
                height = int(height_str) if height_str else None

                # this size is not final yet, because it might contain
                # relative size, not absolute pixels
                temp_size = (width, height,)

                # original size is necessary for relative patterns
                if image and image.size:
                    kwargs.update({'orig_size': image.size})

                # since both absolute and relative patterns are supported,
                # we need to handle conversion based on the type of pattern
                method = getattr(cls, method_name, None)
                if not method:
                    raise AttributeError('%s method not defined' % method_name)

                # this is bound method
                new_size = method(temp_size, image, **kwargs)
                return new_size
        else:  # no pattern found
            raise ValueError("Invalid size pattern")

    @classmethod
    def parse(cls, new_size, image=None, **kwargs):
        '''
        parses new_size and returns a tuple with width and height pixels

        arguments:
            new_size
                Either a tuple, list or string describing the 
                desired size of the picture. For example:
                    1. (800, 600,)
                    2. '800x600'
                    3. '50%'
                    *. (see other examples in ImageSize docstring)
            image
                Reference to PIL Image instance.
                Required for:
                    1. Tuple patterns with one dimension set to None
                    2. Relative string patterns;
                    3. Absolute string patterns when either 
                       width or height is omitted
        '''
                
        if isinstance(new_size, (tuple, list)):
            tuple_size = cls._parse_tuple(new_size, image, **kwargs)
        elif isinstance(new_size, str):
            tuple_size = cls._parse_string(new_size, image, **kwargs)
        else:
            raise TypeError(
                'Invalid size type: only str, tuple and list supported')
        return tuple_size
