# css
from .style import styles, Style, StylesContainer
from .node import CSSNode
from .color import Color

_font_sizes = { # text to points
  'large'  : 13.5,
  'larger' : 14,
  'medium' : 12,
  'small'  : 10,
  'smaller': 10,
  'x-large': 18,
  'x-small': 7.5,
  'xx-large': 24,
  'xx-small': 7,
}

_font_weights = {
  'normal': 400,
  'bold'  : 700,
}

class Font(StylesContainer):
  prefix = 'font'
  subnames = [
    'style',
    'variant', # NOT SUPPORTED
    'weight',
    'stretch', # NOT SUPPORTED
    'size',
    'family',
  ]
  
  def __evaluate_size(self, node):
    size = self.size
    try:
      if isinstance(size, basestring):
        size = size.lower()
        if size == 'inherit':
          parent = node.parent
          if isinstance(parent, CSSNode):
            size = parent.evaluated_style.font.__evaluate_size(parent)
          else:
            raise ValueError('Can\'t inherit font-size from %r' % parent)
        else:
          size = _font_sizes[size]
      elif isinstance(size, int): # TODO px, em, pt classes
        pass # it's OK
      elif isinstance(size, float): # TODO percentage class!
        parent = node.parent
        if isinstance(parent, CSSNode):
          size *= 0.01 * parent.evaluated_style.font.__evaluate_size(parent)
        else:
          raise ValueError('Can\'t inherit font-size from %r' % parent)
      return size
    except KeyError:
      raise ValueError('Unsupported font-size: %r' % size)
  
  def __evaluate_weight(self, node):
    weight = self.weight
    if isinstance(weight, basestring):
      weight = weight.lower()
      if weight == 'inherit':
        parent = node.parent
        if isinstance(parent, CSSNode):
          return parent.evaluated_style.font.__evaluate_weight(parent)
        else:
          raise ValueError('Can\'t inherit font-weight from %r' % parent)
      # TODO implement `lighter`, `bolder`
      else:
        weight = _font_weights.get(weight, -100)
    if   100 <= weight <= 500: return False
    elif 600 <= weight <= 900: return True
    raise ValueError('Unsupported font-weight: %r' % weight)
  
  def __evaluate_style(self, node):
    style = self.style
    if style in ('normal',):
      return False
    elif style in ('italic', 'oblique'):
      return True
    elif style in ('inherit',):
      parent = node.parent
      if isinstance(parent, CSSNode):
        return parent.evaluated_style.font.__evaluate_style(parent)
      else:
        raise ValueError('Can\'t inherit font-style from %r' % parent)
  
  def __evaluate_family(self, node):
    # TODO smart function, testing fonts for existance,
    # handling `inherit` value properly, etc.
    return self.family
  
  # TODO TODO TODO Find a nice way to call this function.
  # Change `CSSNode.apply_style`, maybe?
  def apply_to(self, node):
    if not hasattr(node, 'text_objects'):
      return # nothing to change
    family = self.__evaluate_family(node)
    size   = self.__evaluate_size  (node)
    weight = self.__evaluate_weight(node)
    style  = self.__evaluate_style (node)
    color  = Color(node.evaluated_style['color']) + (255,) # HACK
    for obj in node.text_objects:
      if family:   # HACK complete __evaluate_family and
        obj.font_name = family # you won't need this `if`
      obj.font_size = size
      obj.italic = style
      obj.bold = weight
      obj.color = color


_default_font = Font({
  'style'  : 'normal',
  'variant': 'normal',
  'weight' : 'normal',
  'stretch': 'normal',
  'size'   : 'medium',
  'family' : '' # TODO figure out default pyglet font family
})
Style.subnames.append('font')
Style.subnames.append('color')
Style.defaults['font'] = Font
styles['*'].set_by_subname('font', _default_font)
styles['*'].set_by_subname('color', 'black')