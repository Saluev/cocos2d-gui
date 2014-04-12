from .utility import expand_sided_value, expand_hv_value
from .style import styles, StylesContainer


class BorderImage(StylesContainer):
  prefix = 'image'
  subnames = [
    'source', 'slice', 'width', 'outset', 'repeat'
  ]
  
  # TODO get_as_value, set_to_value
  
  def __init__(self, *args, **kwargs):
    super(BorderImage, self).__init__(*args, **kwargs)
    self.__vertices  = None
    self.__texcoords = None
  
  def __get_image_width(self):
    return expand_sided_value(self.width)
  
  def __get_image_slice(self):
    slice = self.slice
    if isinstance(slice, (tuple, list)) and 'fill' in slice:
      slice = filter(lambda s: s != 'fill', slice) # removing 'fill'
      return (True, ) + expand_sided_value(slice)
    else:
      return (False,) + expand_sided_value(slice)
  
  def __evaluate_image_width(self, node):
    # see developer.mozilla.org/en-US/docs/Web/CSS/border-image-width
    image_width = self.__get_image_width()
    border_width = expand_sided_value(node.evaluated_style['border-width'])
    def evaluate_width(iw, bw):
      if isinstance(iw, int):      # ratio
        return iw * bw
      elif isinstance(iw, float):  # percentage
        return int(iw * bw / 100.)
      else:                        # length (px, em, etc.)
        # TODO TODO handle pixel lengths separately
        raise NotImplementedError
    width = map(evaluate_width, image_width, border_width)
    return width
  
  def __evaluate_image_slice(self, node):
    # see developer.mozilla.org/en-US/docs/Web/CSS/border-image-slice
    # TODO implement `fill` keyword
    assert(self.source != 'none')
    image = self.source
    image_slice = self.__get_image_slice()
    fill, image_slice = image_slice[0], image_slice[1:]
    def evaluate_slice(sl, image_size):
      if isinstance(sl, float):
        return min(image_size, int(image_size * sl / 100.))
      elif isinstance(sl, int):
        return min(image_size, sl)
      raise ValueError
    slice = [ fill,
      evaluate_slice(image_slice[0], image.height), # top
      evaluate_slice(image_slice[1], image.width ), # right
      evaluate_slice(image_slice[2], image.height), # bottom
      evaluate_slice(image_slice[3], image.width ), # left
    ]
    return slice


from .border import Border
Border.subnames.append('image')
Border.defaults['image'] = BorderImage
_default_border = styles['*'].border
_default_border.set_by_subname('image', BorderImage({
  'source': 'none',
  'slice': 100., # TODO percent class?
  'width': 1, # NOT pixels => TODO separate pixel length class
  'outset': 0,
  'repeat': 'stretch',
}))
