# built-in
from collections import defaultdict
# css
from .utility import to_words, from_words
from .utility import expand_sided_value, collapse_sided_value
from .style import styles, Style, StylesContainer, SidedStylesContainer
from . import texturing
from .color import Color


class BorderSide(StylesContainer):
  # prefix = one of 'left', 'top', 'right', 'bottom'
  subnames = [
    'color', 'style', 'width', #'radius'
  ]
  
  def __init__(self, side, *args, **kwargs):
    super(BorderSide, self).__init__(*args, **kwargs)
    assert(side in Border.sides)
    self.prefix = side
    self.__vertices = None
  
  def get_as_value(self):
    width = self.get_by_subname('width')
    style = self.get_by_subname('style')
    color = self.get_by_subname('color')
    return width, style, color
  
  def set_to_value(self, value):
    width, style, color = value
    self.set_by_subname('width', width)
    self.set_by_subname('style', style)
    self.set_by_subname('color', color)
  
  ## drawing functions ##
  def __prepare(self, node):
    border_box = node.border_box
    border = node.evaluated_style.border
    if self.width <= 0 or \
       self.style in ('none', 'hidden') or \
       self.color == 'transparent': # TODO self.color.is_transparent()
      self.__vertices = []
      return
    if self.style not in ('solid', 'hidden', 'inset', 'outset'):
      raise NotImplementedError(
        "%s border style is not yet "
        "implemented" % self.style.title()
      )
    x, y, w, h = border_box
    l, t, r, b = x, y, x + w, y + h
    width, style, color = self.width, self.style, Color(self.color)
    side = self.prefix
    if side == 'left':
      vertices = [(l, t), (l, b), 
        (l + width, b - border.bottom.width),
        (l + width, t + border.top   .width)]
    elif side == 'right':
      vertices = [(r, t), (r, b),
        (r - width, b - border.bottom.width),
        (r - width, t + border.top   .width)]
    elif side == 'bottom':
      vertices = [(l, t), (r, t),
        (r - border.right.width, t + width),
        (l + border.left .width, t + width)]
    elif side == 'top':
      vertices = [(l, b), (r, b),
        (r - border.right.width, b - width),
        (l + border.left .width, b - width)]
    else:
      assert False, '`BorderSide` class seems to be invalid.'
    self.__color = color
    # lightening or darkening color if inset or outset
    if (style, side) in [('inset',  'left' ), ('inset',  'top'   ),
                         ('outset', 'right'), ('outset', 'bottom')]:
      self.__color = color.darken()
    if (style, side) in [('inset',  'right'), ('inset',  'bottom'),
                         ('outset', 'left' ), ('outset', 'top'   )]:
      self.__color = color.lighten()
    self.__vertices_count = len(vertices)
    self.__vertices = texturing.to_buffer(vertices)


class Border(SidedStylesContainer):
  """Object keeping border CSS properties.
  
  >>> b = Border()
  >>> b['border-color'] = '#FFBBFF'
  >>> b['border-left-color']
  '#FFBBFF'
  """
  prefix = 'border'
  defaults = {
    'left'  : lambda: BorderSide('left'  ),
    'top'   : lambda: BorderSide('top'   ),
    'right' : lambda: BorderSide('right' ),
    'bottom': lambda: BorderSide('bottom'),
  }
  sides = SidedStylesContainer.subnames
  subnames = sides + ['image']
  
  def get_as_value(self):
    result = []
    for subname in ('width', 'style', 'color'):
      value = self[(self.prefix, subname)]
      result.append(collapse_sided_value(value))
    return tuple(result)
  
  def set_to_value(self, value):
    for side in self.sides:
      self.get_by_subname(side).set_to_value(value)
  
  def __getitem__(self, which):
    try:
      return super(Border, self).__getitem__(which)
    except KeyError:
      pass # probably, requested border-color or smth like that
    words = to_words(which)
    assert(len(words) == 2)
    modifier = words[1]
    assert(modifier not in self.subnames)
    options = []
    for side in self.sides:
      option = self.get_by_subname(side)[(side, modifier)]
      options.append(option)
    return collapse_sided_value(options)
  
  def __setitem__(self, which, value):
    try:
      return super(Border, self).__setitem__(which, value)
    except KeyError:
      pass
    words = to_words(which)
    assert(len(words) == 2)
    modifier = words[1]
    assert(modifier not in self.subnames)
    values = expand_sided_value(value)
    for side, value in zip(self.sides, values):
      self.get_by_subname(side)[(side, modifier)] = value


_default_border = Border((0, 'none', 'transparent'))
Style.subnames.append('border')
Style.defaults['border'] = Border
styles['*'].set_by_subname('border', _default_border)
