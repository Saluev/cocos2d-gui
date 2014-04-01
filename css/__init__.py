
def to_words(prop):
  return prop.split('-')

def from_words(words):
  words = filter(None, words)
  return '-'.join(words)

from border import Border

_default_style = {
  'width': 'auto',
  'height': 'auto',
  'margin': 0,
  'padding': 0,
  'display': 'block',
  'border': Border(),
  'position': 'static',
  'left': 'auto',
  'top': 'auto',
  # TODO implement CSS3 styles.
}

_shortcuts = {
  'padding-top':    'padding',
  'padding-left':   'padding',
  'padding-right':  'padding',
  'padding-bottom': 'padding',
  
  'margin-top':    'margin',
  'margin-left':   'margin',
  'margin-right':  'margin',
  'margin-bottom': 'margin',
  
  # ... etc.
}


class Style(dict):
  def __getitem__(self, which):
    # 1. The property is set.
    if which in self:
      return super(Style, self).__getitem__(which)
    # 2. The property is not set, but there is a default value,
    if which in _default_style:
      return _default_style[which]
    # 3. There is a shortcut for it.
    if which in _shortcuts:
      return self[_shortcuts[which]]
    # 4. A property of a subobject (e. g. Border) is requested.
    words = to_words(which)
    obj = self.get(words[0], _default_style.get(words[0]))
    if isinstance(obj, dict):
      return obj[which]
    # 5. Not found.
    raise KeyError('No such property: `%s`' % which)
  
  def __setitem__(self, which, value):
    raise NotImplementedError


def _evaluate_node(node):
  parent, style = node.parent, node.style
  left, top = style['left'], style['top']
  left = 0 if left == 'auto' else left
  top  = 0 if top  == 'auto' else top
  position = style['position']
  if position == 'static':
    position_transform = lambda x, y: (x, y)
  elif position == 'relative':
    position_transform = lambda x, y: (x + left, y + top)
  elif position == 'absolute':
    position_transform = lambda x, y: (left, top)
  # TODO fixed?
  margin_offset  = [0, 0]
  border_offset  = [margin_offset[0] + style['margin-left'],
                    margin_offset[1] + style['margin-top' ]]
  padding_offset = [border_offset[0] + style['border-left-width'],
                    border_offset[1] + style['border-top-width' ]]
  content_offset = [padding_offset[0] + style['padding-left'],
                    padding_offset[1] + style['padding-top' ]]
  content_box = content_offset + list(node.get_content_size())
  padding_box = padding_offset + [sum((
    content_box[2],
    style['padding-left'  ],
    style['padding-right' ],
  )), sum((
    content_box[3],
    style['padding-top'   ],
    style['padding-bottom'],
  ))]
  border_box = border_offset + [sum((
    padding_box[2],
    style['border-left-width'  ],
    style['border-right-width' ],
  )), sum((
    padding_box[3],
    style['border-top-width'   ],
    style['border-bottom-width'],
  ))]
  margin_box = margin_offset + [sum((
    border_box[2],
    style['margin-left'  ],
    style['margin-right' ],
  )), sum((
    border_box[3],
    style['margin-top'   ],
    style['margin-bottom'],
  ))]
  width, height = style['width'], style['height'] # TODO percentages?
  width  = margin_box[2] if width  == 'auto' else width
  height = margin_box[3] if height == 'auto' else height
  dw, dh = width - margin_box[2], height - margin_box[3]
  if dw != 0 or dh != 0:
    for box in [margin_box, border_box, padding_box, content_box]:
      box[2] += dw
      box[3] += dh
  info = {
    'node': node,
    'positioning': position_transform,
    'margin_box' : margin_box,
    'border_box' : border_box,
    'padding_box': padding_box,
    'content_box': content_box,
  }
  node.apply_style(**info)


def evaluate(window, element = None):
  element = element or window
  children = element.get_children()
  for child in children:
    assert(child.parent is element)
    evaluate(window, child)
  _evaluate_node(element)


class CSSNode(object):
  def __init__(self, style = None):
    style = style or Style()
    self.style = style
  
  @property
  def width(self):
    if hasattr(self, 'margin_box'):
      return self.margin_box[2]
    if self.style['width'] != 'auto':
      return self.style['width']
    raise NotImplementedError
  
  @property
  def height(self):
    if hasattr(self, 'margin_box'):
      return self.margin_box[3]
    if self.style['height'] != 'auto':
      return self.style['height']
    raise NotImplementedError
  
  def get_content_size(self):
    raise NotImplementedError
  
  def get_children(self):
    raise NotImplementedError
  
  def apply_style(self, **options):
    assert(options.pop('node') == self)
    if not __debug__:
      options.pop('node')
    for key, value in options.iteritems():
      setattr(self, key, value)
    
    

