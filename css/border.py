# built-in
from collections import defaultdict
# css
from . import to_words, from_words
from . import StylesContainer, SidedStylesContainer
from .color import Color


class BorderImage(StylesContainer):
  prefix = 'image'
  defaults = {
    'source': None,
    'slice': 100, # TODO percent
    'width': 1, # NOT pixels => TODO pixels
    'outset': 0,
    'repeat': 'stretch',
  }
  subnames = defaults.keys()


class BorderSide(StylesContainer):
  # prefix = one of 'left', 'top', 'right', 'bottom'
  defaults = {
    'color': 'transparent',
    'style': 'none',
    'width': 0,
    'image': BorderImage,
    'radius': 0,
  }
  subnames = defaults.keys()
  
  #def __new__(cls, side, border = None, *args, **kwargs):
    #assert(side in ['left', 'top', 'right', 'bottom'])
    #result = StylesContainer.__new__(cls, *args, **kwargs)
    #result.prefix = side
    #return result
  
  def __init__(self, side, *args, **kwargs):
    super(BorderSide, self).__init__(*args, **kwargs)
    self.prefix = side
  
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
  
  def _Border__draw(self, border_box, border):
    if self.width <= 0 or \
       self.style == 'none' or \
       self.color == 'transparent': # TODO self.color.is_transparent()
      return
    if self.style != 'solid':
      raise NotImplementedError(
        "%s border style is not yet "
        "implemented" % self.style.title()
      )
    x, y, w, h = border_box
    l, t, r, b = x, y, x + w, y + h
    width, color = self.width, Color(self.color)
    side = self.prefix
    if side == 'left':
      vertices = [(l, t), (l, b), 
        (l + width, b - border.bottom.width),
        (l + width, t + border.top   .width)]
    elif side == 'right':
      vertices = [(r, t), (r, b),
        (r - width, b - border.bottom.width),
        (r - width, t + border.top   .width)]
    elif side == 'top':
      vertices = [(l, t), (r, t),
        (r - border.right.width, t + width),
        (l + border.left .width, t + width)]
    elif side == 'bottom':
      vertices = [(l, b), (r, b),
        (r - border.right.width, b - width),
        (l + border.left .width, b - width)]
    else:
      assert False, '`BorderSide` class seems to be invalid.'
    # running OpenGL render
    from OpenGL import GL
    GL.glPushAttrib(GL.GL_CURRENT_BIT)
    GL.glColor3ubv(color)
    GL.glBegin(GL.GL_QUADS)
    map(GL.glVertex2fv, vertices)
    GL.glEnd()
    GL.glPopAttrib()


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
  
  def get_as_value(self):
    result = []
    for subname in ('width', 'style', 'color'):
      result.append(self[from_words((self.prefix, subname))])
    return tuple(result)
  
  def set_to_value(self, value):
    for side in self.subnames:
      which = from_words((self.prefix, side))
      self[which] = value
  
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
    for side in self.subnames:
      option_name = from_words((self.prefix, side, modifier))
      options.append(self[option_name])
    if len(set(options)) > 1:
      raise ValueError(
        "There are different values for `%s` "
        "property at different sides" % which
      )
    return options.pop()
  
  def __setitem__(self, which, value):
    try:
      return super(Border, self).__setitem__(which, value)
    except KeyError:
      pass
    words = to_words(which)
    assert(len(words) == 2)
    modifier = words[1]
    assert(modifier not in self.subnames)
    for side in self.subnames:
      which = from_words((self.prefix, side, modifier))
      self[which] = value
  
  def draw(self, node):
    box = node.border_box
    self.left  .__draw(box, self)
    self.top   .__draw(box, self)
    self.right .__draw(box, self)
    self.bottom.__draw(box, self)
    
  
  



