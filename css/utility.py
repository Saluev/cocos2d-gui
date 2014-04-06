from collections import defaultdict

def to_words(prop):
  if isinstance(prop, basestring):
    return prop.split('-')
  else:
    # an iterable already
    return list(prop)

def from_words(words):
  words = filter(None, words)
  return '-'.join(words)

def expand_sided_value(value):
  """Returns 4-tuple with values corresponding
  to top, right, bottom, and left.
  
  Possible inputs:
  style                  /* One-value syntax   */  E.g. 1em; 
  vertical horizontal    /* Two-value syntax   */  E.g. 5% auto; 
  top horizontal bottom  /* Three-value syntax */  E.g. 1em auto 2em; 
  top right bottom left  /* Four-value syntax  */  E.g. 2px 1em 0 auto; 
  """
  if not isinstance(value, (tuple, list)):
    return (value,) * 4
  elif len(value) == 1:
    return tuple(value) * 4
  elif len(value) == 2:
    vertical, horizontal = value
    return (vertical, horizontal) * 2
  elif len(value) == 3:
    top, horizontal, bottom = value
    return (top, horizontal, bottom, horizontal)
  elif len(value) == 4:
    return tuple(value)
  else:
    raise ValueError('Invalid collapsed four-sided value: %r' % value)

def collapse_sided_value(value):
  """Inverses `expand_sided_value`, returning
  the most optimal form of four-sided value.
  """
  if not isinstance(value, (tuple, list)):
    return value
  elif len(value) == 1:
    return value[0]
  elif len(value) == 2:
    if value[0] == value[1]:
      return value[0]
    else:
      return tuple(value)
  elif len(value) == 3:
    if value[0] == value[2]:
      return collapse_sided_value(value[0:2])
    else:
      return tuple(value)
  elif len(value) == 4:
    if value[1] == value[3]:
      return collapse_sided_value(value[0:3])
    else:
      return tuple(value)
  else:
    raise ValueError('Invalid expanded four-sided value: %r' % value)
