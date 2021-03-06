from .utility import to_words, from_words
from .style import styles, Style, StylesContainer
from .color import Color
from . import texturing

# TODO support FUCKING MORE features of CSS3 `background` property

class Background(StylesContainer):
  prefix = 'background'
  subnames = [
    'color', 'position', 'size',
    'repeat', 'origin', 'clip', 'image'
  ]
  
  def get_as_value(self):
    return tuple(map(self.get_by_subname, self.subnames))
  
  def set_to_value(self, values):
    if not isinstance(values, tuple):
      values = (values,)
    for value in values:
      try:
        color = Color(value)
        self.color = value # TODO self.color = color, and full-featured Color object
        continue
      except ValueError:
        pass
      # TODO other properties
      # try...
      raise NotImplementedError
  
  def draw(self): # TODO move to `rendering.py`
    node = self.node
    # WARNING using background-origin here, but
    # it won't work for `initial` and `inherit`
    x, y, w, h = getattr(node, self.origin.replace('-', '_'))
    l, t, r, b = x, y, x + w, y + h
    color = Color(self.color)
    from OpenGL import GL
    if not color.is_transparent():
      GL.glPushAttrib(GL.GL_CURRENT_BIT)
      GL.glColor4ubv(color)
      GL.glBegin(GL.GL_QUADS)
      vertices = [(l, t), (l, b), (r, b), (r, t)]
      map(GL.glVertex2fv, vertices)
      GL.glEnd()
      GL.glPopAttrib()
    if self.image == 'none':
      return
    iw, ih = self.image.width, self.image.height
    size = self.size
    if size == 'auto':
      tile_size = iw, ih
    elif size == 'cover':
      scale = max(w / float(iw), h / float(ih))
      tile_size = int(iw * scale), int(ih * scale)
    elif size == 'contain':
      scale = min(w / float(iw), h / float(ih))
      tile_size = int(iw * scale), int(ih * scale)
    elif isinstance(size, (int, float, tuple)):
      if isinstance(size, (int, float)):
        mw = mh = size
      else:
        mw, mh = size
      if isinstance(mw, int) and isinstance(mh, int):
        pass
      elif isinstance(mw, float) and isinstance(mh, float): # TODO percent class
        mw = int(iw * (mw * 0.01))
        mh = int(ih * (mh * 0.01))
      else:
        raise ValueError(
          'Invalid value for background-size: %r' % size
        )
      tile_size = mw, mh
    
    repeat = self.repeat
    if repeat == 'repeat':
      bg_size = w, h
    elif repeat == 'repeat-x':
      bg_size = w, tile_size[1]
    elif repeat == 'repeat-y':
      bg_size = tile_size[0], h
    elif repeat == 'no-repeat':
      bg_size = tile_size
    else:
      raise ValueError(
        'Invalid value for background-repeat: %r' % repeat
      )
    
    # TODO: implement background-position, background-clip
    texture = self.image.get_texture()
    tilew, tileh = tile_size
    bgw, bgh = bg_size
    
    texturing.tile(texture, (l, t, bgw, bgh), tile_size)
    # TODO bufferize computations to improve performance
    # using tile(..., action='evaluate')


Style.subnames.append('background')
Style.defaults['background'] = Background
styles['*'].set_by_subname('background', Background({
  'color' : 'transparent',
  'position': (0., 0.), # TODO percent class?
  'size'  : 'auto',
  'repeat': 'repeat',
  'origin': 'padding-box',
  'clip'  : 'border-box',
  'image' : 'none'
}))