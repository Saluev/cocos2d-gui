import re

_hex_color = re.compile('^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$')

# TODO color class!

def Color(s):
  hex_match = _hex_color.match(s)
  if hex_match is not None:
    hex_color = hex_match.group(1)
    if len(hex_color) == 6:
      r = int(hex_color[0:2], 16)
      g = int(hex_color[2:4], 16)
      b = int(hex_color[4:6], 16)
    elif len(hex_color) == 3:
      r = int(hex_color[0], 16) * (16 + 1)
      g = int(hex_color[1], 16) * (16 + 1)
      b = int(hex_color[2], 16) * (16 + 1)
    else:
      assert False, '`_hex_color` regexp seems to be invalid.'
    return r, g, b
  raise NotImplementedError(
    "Only #RRGGBB format is currently "
    "implemented for color."
  )
  