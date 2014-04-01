from . import to_words, from_words

_border_sides = [
  'top', 'bottom',
  'left', 'right',
]

_border_modifiers = [
  'color',
  'style',
  'width',
  'image',
  'radius',
]

_border_defaults = {
  'color': None,
  'style': 'none',
  'width': 0,
  'image': None, # TODO BorderImage class
  'radius': 0,
}

def _modifier(words):
  return words[-1] if words[-1] in _border_modifiers else None

def _side(words):
  return words[1] if len(words) > 1 and words[1] in _border_sides else None


class Border(dict):
  """Object keeping border CSS properties.
  
  >>> b = Border()
  >>> b['border-color'] = '#FFBBFF'
  >>> b['border-left-color']
  '#FFBBFF'
  """
  def __getitem__(self, which):
    if which in self:
      return super(Border, self).__getitem__(which)
    words = to_words(which)
    assert(words[0] == 'border')
    if 'image' in words:
      # BorderImage subobject-related data requested
      if which == 'border-image':
        return self.get('border-image', _border_defaults['image'])
      return self['border-image'][which]
    modifier = _modifier(words)
    side = _side(words)
    if not modifier and not side:
      raise KeyError('No such property: `%s`' % which)
    if not modifier:
      # whole border data is requested for some side
      wproperty = from_words(('border', side, 'width'))
      sproperty = from_words(('border', side, 'style'))
      cproperty = from_words(('border', side, 'color'))
      return (self[wproperty], self[sproperty], self[cproperty])
    if not side:
      # some data for all parts is requested
      values = []
      for side in _border_sides:
        curr_property = from_words(('border', side, modifier))
        values.append(self[curr_property])
      if len(set(values)) > 1:
        raise ValueError(
          "There are different values for `%s` "
          "property at different sides" % which
        )
      return values[0]
    # a very particular data requested but not found
    common_property = from_words(('border', modifier))
    if common_property in self:
      return self[common_property]
    # nothing works
    return _border_defaults[modifier]
  
  def __setitem__(self, which, value):
    words = to_words(which)
    assert(words[0] == 'border')
    modifier = _modifier(words)
    side = _side(words)
    if not modifier:
      # a bunch of data
      width, style, color = value
      wproperty = from_words(('border', side, 'width'))
      sproperty = from_words(('border', side, 'style'))
      cproperty = from_words(('border', side, 'color'))
      self[wproperty] = width
      self[sproperty] = style
      self[cproperty] = color
      return
    super(Border, self).__setitem__(which, value)





