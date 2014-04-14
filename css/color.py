import re, colorsys

_float = '(?:[-+]?(?:\d*\.\d+|\d+\.\d*|\d+)(?:[eE][-+]?\d+)?)'

_hex_color  = re.compile('^#?([0-9a-fA-F]{6}|[0-9a-fA-F]{3})$')
_hsl_color  = re.compile(
    '^hsl\(\s*(\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*\)$')
_rgb_color  = re.compile(
    '^rgb\(\s*(\d+%?)\s*,\s*(\d+%?)\s*,\s*(\d+%?)\s*\)$')
_rgba_color = re.compile(
    '^rgba\(\s*(\d+%%?)\s*,\s*(\d+%%?)\s*,\s*(\d+%%?)\s*,'
    '\s*(%s)\s*\)$' % _float)
_hsla_color = re.compile(
    '^hsla\(\s*(\d+)\s*,\s*(\d+)%%\s*,\s*(\d+)%%\s*,'
    '\s*(%s)\s*\)$' % _float)

def clamp(what, minv, maxv):
  return max(minv, min(maxv, what))

def _clamp_to_ubyte(what):
  return clamp(int(round(what)), 0, 255)

def _raw_to_ubyte(s):
  if '%' in s:
    result = int(int(s[:-1]) * 2.55 + 0.5) # rounding
    return _clamp_to_ubyte(result)
  else:
    return _clamp_to_ubyte(int(s))

def hsl_to_rgb(h, s, l):
  """Converts HSL as it was obtained from CSS to valid RGB."""
  h, s, l = h / 360., s / 100., l / 100.
  r, g, b = colorsys.hls_to_rgb(h, l, s)
  r, g, b = int(255 * r), int(255 * g), int(255 * b)
  r, g, b = map(_clamp_to_ubyte, (r, g, b))
  return r, g, b

# thanks http://www.yourhtmlsource.com/stylesheets/namedcolours.html
# for this color table
_named_colors = {
  'Aliceblue': 'F0F8FF',
  'Antiquewhite': 'FAEBD7',
  'Aqua': '00FFFF',
  'Aquamarine': '7FFFD4',
  'Azure': 'F0FFFF',
  'Beige': 'F5F5DC',
  'Bisque': 'FFE4C4',
  'Black': '000000',
  'Blanchedalmond': 'FFEBCD',
  'Blue': '0000FF',
  'Blueviolet': '8A2BE2',
  'Brown': 'A52A2A',
  'Burlywood': 'DEB887',
  'Cadetblue': '5F9EA0',
  'Chartreuse': '7FFF00',
  'Chocolate': 'D2691E',
  'Coral': 'FF7F50',
  'Cornflowerblue': '6495ED',
  'Cornsilk': 'FFF8DC',
  'Crimson': 'DC143C',
  'Cyan': '00FFFF',
  'Darkblue': '00008B',
  'Darkcyan': '008B8B',
  'Darkgoldenrod': 'B8860B',
  'Darkgray': 'A9A9A9',
  'Darkgreen': '006400',
  'Darkkhaki': 'BDB76B',
  'Darkmagenta': '8B008B',
  'Darkolivegreen': '556B2F',
  'Darkorange': 'FF8C00',
  'Darkorchid': '9932CC',
  'Darkred': '8B0000',
  'Darksalmon': 'E9967A',
  'Darkseagreen': '8FBC8F',
  'Darkslateblue': '483D8B',
  'Darkslategray': '2F4F4F',
  'Darkturquoise': '00CED1',
  'Darkviolet': '9400D3',
  'Deeppink': 'FF1493',
  'Deepskyblue': '00BFFF',
  'Dimgray': '696969',
  'Dodgerblue': '1E90FF',
  'Firebrick': 'B22222',
  'Floralwhite': 'FFFAF0',
  'Forestgreen': '228B22',
  'Fuchsia': 'FF00FF',
  'Gainsboro': 'DCDCDC',
  'Ghostwhite': 'F8F8FF',
  'Gold': 'FFD700',
  'Goldenrod': 'DAA520',
  'Gray': '808080',
  'Green': '008000',
  'Greenyellow': 'ADFF2F',
  'Honeydew': 'F0FFF0',
  'Hotpink': 'FF69B4',
  'Indianred': 'CD5C5C',
  'Indigo': '4B0082',
  'Ivory': 'FFFFF0',
  'Khaki': 'F0E68C',
  'Lavender': 'E6E6FA',
  'Lavenderblush': 'FFF0F5',
  'Lawngreen': '7CFC00',
  'Lemonchiffon': 'FFFACD',
  'Lightblue': 'ADD8E6',
  'Lightcoral': 'F08080',
  'Lightcyan': 'E0FFFF',
  'Lightgoldenrodyellow': 'FAFAD2',
  'Lightgreen': '90EE90',
  'Lightgray': 'D3D3D3',  # because I think it is correct
  'Lightgrey': 'D3D3D3',
  'Lightpink': 'FFB6C1',
  'Lightsalmon': 'FFA07A',
  'Lightseagreen': '20B2AA',
  'Lightskyblue': '87CEFA',
  'Lightslategray': '778899',
  'Lightsteelblue': 'B0C4DE',
  'Lightyellow': 'FFFFE0',
  'Lime': '00FF00',
  'Limegreen': '32CD32',
  'Linen': 'FAF0E6',
  'Magenta': 'FF00FF',
  'Maroon': '800000',
  'Mediumauqamarine': '66CDAA',
  'Mediumblue': '0000CD',
  'Mediumorchid': 'BA55D3',
  'Mediumpurple': '9370D8',
  'Mediumseagreen': '3CB371',
  'Mediumslateblue': '7B68EE',
  'Mediumspringgreen': '00FA9A',
  'Mediumturquoise': '48D1CC',
  'Mediumvioletred': 'C71585',
  'Midnightblue': '191970',
  'Mintcream': 'F5FFFA',
  'Mistyrose': 'FFE4E1',
  'Moccasin': 'FFE4B5',
  'Navajowhite': 'FFDEAD',
  'Navy': '000080',
  'Oldlace': 'FDF5E6',
  'Olive': '808000',
  'Olivedrab': '688E23',
  'Orange': 'FFA500',
  'Orangered': 'FF4500',
  'Orchid': 'DA70D6',
  'Palegoldenrod': 'EEE8AA',
  'Palegreen': '98FB98',
  'Paleturquoise': 'AFEEEE',
  'Palevioletred': 'D87093',
  'Papayawhip': 'FFEFD5',
  'Peachpuff': 'FFDAB9',
  'Peru': 'CD853F',
  'Pink': 'FFC0CB',
  'Plum': 'DDA0DD',
  'Powderblue': 'B0E0E6',
  'Purple': '800080',
  'Red': 'FF0000',
  'Rosybrown': 'BC8F8F',
  'Royalblue': '4169E1',
  'Saddlebrown': '8B4513',
  'Salmon': 'FA8072',
  'Sandybrown': 'F4A460',
  'Seagreen': '2E8B57',
  'Seashell': 'FFF5EE',
  'Sienna': 'A0522D',
  'Silver': 'C0C0C0',
  'Skyblue': '87CEEB',
  'Slateblue': '6A5ACD',
  'Slategray': '708090',
  'Snow': 'FFFAFA',
  'Springgreen': '00FF7F',
  'Steelblue': '4682B4',
  'Tan': 'D2B48C',
  'Teal': '008080',
  'Thistle': 'D8BFD8',
  'Tomato': 'FF6347',
  'Turquoise': '40E0D0',
  'Violet': 'EE82EE',
  'Wheat': 'F5DEB3',
  'White': 'FFFFFF',
  'Whitesmoke': 'F5F5F5',
  'Yellow': 'FFFF00',
  'YellowGreen': '9ACD32',
  'transparent': 'rgba(0, 0, 0, 0)'
}


class Color(tuple):
  def __new__(cls, s):
    if isinstance(s, (tuple, list)):
      s = map(_clamp_to_ubyte, s)
      return tuple.__new__(cls, s)
    if not isinstance(s, basestring):
      raise TypeError('Invalid CSS color value: %r' % s)
    s = s.lower().strip()
    ## checking simple names ##
    if s in _named_colors:
      return cls.__new__(cls, _named_colors[s])
    try:
      a = 255 # default alpha value
      ## checking hex RGB triple ##
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
        return tuple.__new__(cls, (r, g, b, a))
      ## checking RGB
      rgb_match = _rgb_color.match(s)
      if rgb_match is not None:
        r, g, b = map(_raw_to_ubyte, rgb_match.groups())
        return tuple.__new__(cls, (r, g, b, a))
      ## checking RGBA ##
      rgba_match = _rgba_color.match(s)
      if rgba_match is not None:
        r, g, b, a = rgba_match.groups()
        r, g, b = map(_raw_to_ubyte, (r, g, b))
        a = int(float(a) * 255 + 0.5)
        return tuple.__new__(cls, (r, g, b, a))
      ## checking HSL ##
      hsl_match = _hsl_color.match(s)
      if hsl_match is not None:
        h, s, l = map(int, hsl_match.groups())
        r, g, b = hsl_to_rgb(h, s, l)
        return tuple.__new__(cls, (r, g, b, a))
      ## checking HSLA ##
      hsla_match = _hsla_color.match(s)
      if hsla_match is not None:
        h, s, l, a = hsla_match.groups()
        r, g, b = hsl_to_rgb(int(h), int(s), int(l))
        a = int(float(a) * 255 + 0.5)
        return tuple.__new__(cls, (r, g, b, a))
      # nothing worked
      raise ValueError
    except ValueError:
      raise ValueError('Invalid CSS color: %r' % s)
  
  def is_transparent(self):
    return (self.alpha == 0)
  
  # TODO: properties like red, green, blue, hue, saturation, ...
  
  @property
  def alpha(self):
    return self[3]
  
  def scale(self, mpr):
    r, g, b = self[:3]
    r, g, b = mpr * r, mpr * g, mpr * b
    return Color((r, g, b, self.alpha))
  
  def lighten(self, strength=0.2):
    return self.scale(1.0 + strength)
  
  def darken(self, strength=0.2):
    return self.scale(1.0 - strength)


_named_colors = {k.lower(): Color(v) for k, v in _named_colors.items()}
