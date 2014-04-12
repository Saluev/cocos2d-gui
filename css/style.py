from collections import defaultdict
from utility import to_words, from_words
from utility import expand_sided_value, collapse_sided_value

class StylesContainer(dict):
  
  # e. g. 'border', 'padding', etc.
  prefix = None
  
  # names that are available within prefix,
  # e. g. 'color' (full name 'border-color').
  subnames = []
  
  # default values for properties
  defaults = {}
  
  def __init__(self, something = None, **kwargs):
    self.node = None
    if isinstance(something, dict):
      super(StylesContainer, self).__init__(something, **kwargs)
    else:
      super(StylesContainer, self).__init__(**kwargs)
      if something is not None:
        self.set_to_value(something)
  
  def apply_to(self, node):
    self.node = node
    for subitem in self.values():
      if isinstance(subitem, StylesContainer):
        subitem.apply_to(node)
  
  def __str__(self):
    try:
      as_value = self.get_as_value()
      if as_value == self:
        return repr(self)
      return str(as_value)
    except (NotImplementedError, ValueError):
      return repr(self)
  
  def __repr__(self):
    return '%s(%s)' % (type(self).__name__, dict.__repr__(self))
  
  def get_as_value(self):
    """Returns CSS representation of the whole style object.
    
    >>> Border().get_as_value()
    (0, 'none', 'transparent')
    """
    raise NotImplementedError # abstract
  
  def set_to_value(self, value):
    """Gets style object from representation.
    
    >>> b = Border()
    >>> b = 1, 'solid', 'black'
    >>> b['border-style']
    'solid'
    """
    raise NotImplementedError # abstract
  
  def on_change(self):
    pass
  
  def create_default(self, subname):
    default = self.defaults.get(subname)
    if hasattr(default, '__call__'):
      result = default()
      self.set_by_subname(subname, result)
      return result
    else:
      return None
  
  def get_by_subname(self, subname):
    if subname not in self.subnames:
      raise KeyError(
        '%r not in %s' % (subname, self.prefix or 'style'))
    subobject = super(StylesContainer, self).get(subname)
    if subobject is None:
      subobject = self.create_default(subname)
    return subobject
  
  def set_by_subname(self, subname, value):
    if subname not in self.subnames:
      raise KeyError(
        '%r not in %s' % (subname, self.prefix or 'style'))
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
      return subobject[words[1:]]
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
    currobject = self.get_by_subname(subname)
    if isinstance(currobject, StylesContainer):
      currobject[words[1:]] = value
    else:
      self.set_by_subname(subname, value)
    self.on_change()
  
  def __getattr__(self, which):
    try:
      return super(StylesContainer, self).__getattr__(self, which)
    except AttributeError:
      return self.get_by_subname(which)
  
  def update(self, other):
    for key, value in other.items():
      if isinstance(value, StylesContainer):
        own = self.get_by_subname(key)
        if own is None:
          self.set_by_subname(key, value)
        else:
          own.update(value)
      else:
        self.set_by_subname(key, value)


class SidedStylesContainer(StylesContainer):
  subnames = ['top', 'right', 'bottom', 'left']
  # WARNING: order is important here. this order
  # corresponds to CSS specifications.


class _AbstractIndent(SidedStylesContainer):
  def get_as_value(self):
    values = map(self.get_by_subname, self.subnames)
    if None in values:
      raise ValueError
    return collapse_sided_value(values)
  
  def set_to_value(self, value):
    value = expand_sided_value(value)
    for i, subname in enumerate(self.subnames):
      self.set_by_subname(subname, value[i])


class Margin(_AbstractIndent):
  prefix = 'margin'


class Padding(_AbstractIndent):
  prefix = 'padding'


class Style(StylesContainer):
  defaults = {
    'margin' : Margin,
    'padding': Padding,
  }
  subnames = [
    'display', 'position',
    'left', 'top', 'width', 'height',
    'margin', 'padding',
  ]
  
  def get_as_value(self):
    return self
  
  def set_to_value(self, value):
    self.update(value)


styles = defaultdict(Style)

styles['*'] = Style({
    'width': 'auto',
    'height': 'auto',
    'margin': Margin(0),
    'padding': Padding(0),
    'display': 'block',
    'position': 'static',
    'left': 'auto',
    'top': 'auto',
})
