from . import to_words, from_words, StylesContainer
from .color import Color


class Background(StylesContainer):
  prefix = 'background'
  defaults = {
    'color': 'transparent',
    'position': (0., 0.), # TODO percent class?
    'size': 'auto',
    'repeat': 'repeat',
    'origin': 'padding-box',
    'clip': 'border-box',
   #'attachment': 'scroll',
    'image': 'none',
  }
  subnames = defaults.keys()
  
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
  
  def draw(self, node):
    # WARNING using background-origin here, but
    # it won't work for `initial` and `inherit`
    x, y, w, h = getattr(node, self.origin.replace('-', '_'))
    l, t, r, b = x, y, x + w, y + h
    from OpenGL import GL
    if self.color != 'transparent': # TODO self.color.is_transparent()
      color = Color(self.color)
      GL.glPushAttrib(GL.GL_CURRENT_BIT)
      GL.glColor3ubv(color)
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
    # the following code is a hack assuming our texture is
    # just a _rectangular_ piece of another texture.
    # TODO: implement for arbitrary texture.tex_coords.
    if not __debug__: # this is the most concrete 'todo' in Python
      raise NotImplementedError(
        'Handling arbitrary texcoords in `Background.draw` '
        'not implemented yet!'
      )
    tcl, tct, tcr, tcb = map(texture.tex_coords.__getitem__, (0, 7, 6, 1))
    tilew, tileh = tile_size
    bgw, bgh = bg_size
    
    # TODO bufferize all these computations to improve performance
    vertices  = []
    texcoords = []
    drawnw = 0
    while drawnw < bgw:
      currtilew = min(tilew, bgw - drawnw)
      currtcw = (tcr - tcl) * currtilew / float(tilew)
      drawnh = 0
      while drawnh < bgh:
        currtileh = min(tileh, bgh - drawnh)
        currtch = (tct - tcb) * currtileh / float(tileh)
        vertices.extend([
          (l + drawnw, t + drawnh),
          (l + drawnw + currtilew, t + drawnh),
          (l + drawnw + currtilew, t + drawnh + currtileh),
          (l + drawnw, t + drawnh + currtileh)
        ])
        texcoords.extend([
          (tcl, tct),
          (tcl + currtcw, tct),
          (tcl + currtcw, tct - currtch),
          (tcl, tct - currtch)
        ])
        drawnh += currtileh
      drawnw += currtilew
    
    GL.glPushAttrib(GL.GL_ENABLE_BIT | GL.GL_TEXTURE_BIT | GL.GL_CURRENT_BIT)
    GL.glEnable(texture.target)
    GL.glBindTexture(texture.target, texture.id)
    GL.glBegin(GL.GL_QUADS)
    for vertex, texcoord in zip(vertices, texcoords):
      GL.glTexCoord2fv(texcoord)
      GL.glVertex2fv(vertex)
    GL.glEnd()
    GL.glPopAttrib()
    
    #if __debug__:
      #GL.glPushAttrib(GL.GL_CURRENT_BIT)
      #GL.glDisable(texture.target)
      #GL.glColor3ub(255, 255, 0)
      #GL.glBegin(GL.GL_LINES)
      #map(GL.glVertex2fv, vertices)
      #GL.glEnd()
      #GL.glPopAttrib()
    
    
    
    