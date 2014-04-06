from .style import styles, Style


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
    print(style)
  
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


def _shift_box(box, xy):
  return (
    box[0] + xy[0],
    box[1] + xy[1],
    box[2], box[3],
  )
