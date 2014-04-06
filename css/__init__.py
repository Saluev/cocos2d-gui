from collections import defaultdict

def to_words(prop):
  return prop.split('-')

def from_words(words):
  words = filter(None, words)
  return '-'.join(words)


class StylesContainer(dict):
  
  # e. g. 'border', 'padding', etc.
  prefix = None
  
  # names that are available within prefix,
  # e. g. 'color' (full name 'border-color').
  subnames = []
  
  # default values for properties
  defaults = {}
  
  def __str__(self):
    try:
      return str(self.get_as_value())
    except (NotImplementedError, ValueError):
      return repr(self)
  
  def __repr__(self):
    return '%s(%s)' % (type(self).__name__, dict.__repr__(self))
  
  def get_as_value(self):
    # abstract
    raise NotImplementedError
  
  def set_to_value(self, value):
    # abstract
    raise NotImplementedError
  
  def on_change(self):
    pass
  
  def get_default(self, subname):
    default = self.defaults[subname]
    if type(default) == type or type(default) == type(lambda:None):
      return default()
    else:
      return default
  
  def get_by_subname(self, subname):
    if subname not in self.subnames:
      raise KeyError(subname)
    subobject = super(StylesContainer, self).get(subname)
    if subobject is None:
      subobject = self.get_default(subname)
      self.set_by_subname(subname, subobject)
    return subobject
  
  def set_by_subname(self, subname, value):
    if subname not in self.subnames:
      raise KeyError(subname)
    super(StylesContainer, self).__setitem__(subname, value)
  
  def __getitem__(self, which):
    words = to_words(which)
    if self.prefix is None:
      words = [None] + words
    assert(words[0] == self.prefix)
    if len(words) == 1:
      return self.get_as_value()
    subname = words[1]
    subobject = self.get_by_subname(subname)
    if isinstance(subobject, StylesContainer):
      return subobject[from_words(words[1:])]
    elif len(words) == 2:
      return subobject
    else:
      raise KeyError(which)
  
  def __setitem__(self, which, value):
    words = to_words(which)
    if self.prefix is None:
      words = [None] + words
    assert(words[0] == self.prefix)
    if len(words) == 1:
      self.set_to_value(value)
      return
    subname = words[1]
    # the following also creates a new object if necessary
    currobject = self.get_by_subname(subname)
    if isinstance(currobject, StylesContainer):
      currobject[from_words(words[1:])] = value
    else:
      self.set_by_subname(subname, value)
    self.on_change()
  
  def __getattr__(self, which):
    try:
      return super(StylesContainer, self).__getattr__(self, which)
    except AttributeError:
      return self.get_by_subname(which)


class SidedStylesContainer(StylesContainer):
  subnames = ['top', 'right', 'bottom', 'left']
  # WARNING: order is important here. this order
  # corresponds to CSS specifications.


class CumulativeStylesContainer(StylesContainer):
  def get_as_value(self):
    #import ipdb; ipdb.set_trace()
    values = map(self.get_by_subname, self.subnames)
    if len(set(values)) != 1:
      raise ValueError(
        'Can\'t return cumulative value `%s`' % self.prefix
      )
    return values.pop()
  
  def set_to_value(self, value):
    for subname in self.subnames:
      self.set_by_subname(subname, value)


class Margin(SidedStylesContainer, CumulativeStylesContainer):
  prefix = 'margin'
  defaults = defaultdict(int)


class Padding(SidedStylesContainer, CumulativeStylesContainer):
  prefix = 'padding'
  defaults = defaultdict(int)


from border import Border
from background import Background


class Style(StylesContainer):
  defaults = {
    'width': 'auto',
    'height': 'auto',
    'margin': Margin,
    'padding': Padding,
    'display': 'block',
    'border': Border,
    'position': 'static',
    'left': 'auto',
    'top': 'auto',
    'background': Background,
  }
  subnames = defaults.keys()
  
  def get_as_value(self):
    return self
  
  def set_to_value(self, value):
    self.update(value)


styles = defaultdict(Style)


def _evaluate_node(node):
  node.evaluate_style()
  parent, style = node.parent, node.evaluated_style
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
  if element is None:
    element = window
  children = element.get_nodes()
  for child in children:
    assert(child.parent is element)
    evaluate(window, child)
  _evaluate_node(element)

def _shift_box(box, xy):
  return (
    box[0] + xy[0],
    box[1] + xy[1],
    box[2], box[3],
  )


class CSSNode(object):
  
  def __init__(self, style = None):
    self.id = '%x' % id(self)
    style = style or Style()
    self.style = style
    self.__evaluated_style = None
    self.state = set()
    self.positioning = lambda x, y: (x, y)
  
  def clear(self):
    self.__evaluated_style = None
    self.order()
  
  def add_state(self, state):
    self.state.add(state)
    self.clear()
  
  def remove_state(self, state):
    if state in self.state:
      self.state.remove(state)
      self.clear()
  
  def evaluate_style(self):
    id_query = '#' + self.id
    classes = type(self).mro()
    class_names   = (cls.__name__ for cls in classes if issubclass(cls, CSSNode))
    class_queries = map('.'.__add__, class_names)[::-1]
    style = Style()
    # common stylesheet
    applicable_styles = ['*']
    # class-specific stylesheets
    for query in class_queries:
      applicable_styles.append(query)
      applicable_styles.extend(query + ':' + pseudo for pseudo in self.state)
    # object-specific stylesheets
    applicable_styles.append(id_query)
    applicable_styles.extend(id_query + ':' + pseudo for pseudo in self.state)
    # now collecting all together
    print(applicable_styles)
    for applicable_style in applicable_styles:
      style.update(styles[applicable_style])
    self.evaluated_style = style
  
  @property
  def evaluated_style(self):
    if self.__evaluated_style is not None:
      return self.__evaluated_style
    from logging import warn
    warn('Trying to access `CSSNode.evaluated_style` '
         'before it was actually evaluated')
    return styles['#' + self.id]
  
  @evaluated_style.setter
  def evaluated_style(self, style):
    self.__evaluated_style = style
  
  @property
  def style(self):
    return styles['#' + self.id]
  
  @style.setter
  def style(self, value):
    styles['#' + self.id] = value
  
  def pseudostyle(self, which):
    return styles['#%s:%s' % (self.id, which)]
  
  @property
  def width(self):
    if hasattr(self, 'margin_box'):
      return self.margin_box[2]
    if self.evaluated_style['width'] != 'auto':
      return self.evaluated_style['width']
    raise NotImplementedError
  
  @property
  def height(self):
    if hasattr(self, 'margin_box'):
      return self.margin_box[3]
    if self.evaluated_style['height'] != 'auto':
      return self.evaluated_style['height']
    raise NotImplementedError
  
  def get_content_size(self):
    raise NotImplementedError
  
  def get_nodes(self):
    raise NotImplementedError
  
  def apply_style(self, **options):
    assert(options.pop('node') == self)
    if not __debug__:
      options.pop('node')
    for key, value in options.iteritems():
      setattr(self, key, value)
  
  def set_position(self, x, y):
    position = self.positioning(x, y)
    if hasattr(self, 'position'):
      self.position = position
    self.margin_box  = _shift_box(self.margin_box , position)
    self.padding_box = _shift_box(self.padding_box, position)
    self.border_box  = _shift_box(self.border_box , position)
    self.content_box = _shift_box(self.content_box, position)

