import operator

def rect_from_sides(left, top, right, bottom):
  """Returns list of points of a rectangle
  defined by it's `left`, `top`, `right`, and `bottom`
  coordinates, ordered counter-clockwise."""
  return [
    (left,  bottom),
    (right, bottom),
    (right, top   ),
    (left,  top   ),
  ]

def _vectorize(op, name = None, doc = None):
  def fn(self, other):
    if isinstance(other, (tuple, list)):
      return vector(map(op, self, other))
    else:
      return vector(op(item, other) for item in self)
  if name:
    fn.__name__ = name
  if doc:
    fn.__doc__ = doc
  return fn

def _reverse(op):
  def fn(*args): return op(*args[::-1])
  return fn


class vector(tuple):
  """The simpliest vector class possible."""
  __add__  = _vectorize(operator.add, '__add__')
  __sub__  = _vectorize(operator.sub, '__sub__')
  __mul__  = _vectorize(operator.mul, '__mul__')
  __div__  = _vectorize(operator.div, '__div__')
  __radd__ = _vectorize(_reverse(operator.add), '__radd__')
  __rsub__ = _vectorize(_reverse(operator.sub), '__rsub__')
  __rmul__ = _vectorize(_reverse(operator.mul), '__rmul__')
  __rdiv__ = _vectorize(_reverse(operator.div), '__rdiv__')
  
  def __abs__(self):
    """Computes euclidian length of a vector."""
    return sum(abs(item) ** 2 for item in self) ** 0.5


_default_texcoords = [
  (0., 0.), (1., 0.), (1., 1.), (0., 1.)
]

def tile(texture, rect, tile_size=None,
         texcoords=_default_texcoords, action='draw'):
  if action not in ('evaluate', 'draw'):
    raise ValueError('Invalid action for `tile`: %r' % action)
  if tile_size is None:
    tile_size = texture.width, texture.height
  l, t, bgw, bgh = rect
  tilew, tileh = tile_size
  
  if not __debug__:
    raise NotImplementedError(
      'Handling arbitrary texcoords in `BorderImage.draw` '
      'not implemented yet!')
  # corners of texture itself
  tbl = vector(texture.tex_coords[0:][:2])
  tbr = vector(texture.tex_coords[3:][:2])
  ttr = vector(texture.tex_coords[6:][:2])
  ttl = vector(texture.tex_coords[9:][:2])
  tbasis = (tbl, tbr - tbl, ttl - tbl)
  assert(abs(tbasis[0] + tbasis[1] + tbasis[2] - ttr) < 1E-6)
  # (in other case our computations would be way too difficult.)
  
  def tc(what, basis = tbasis):
    return basis[0] + what[0] * basis[1] + what[1] * basis[2]
  
  # texcoords for contraction requested by user
  tbl, tbr, ttr, ttl = map(tc, texcoords)
  
  ubasis = (ttl, ttr - ttl, tbl - ttl)
  assert(abs(ubasis[0] + ubasis[1] + ubasis[2] - tbr) < 1E-6)
  # (in other case our computations would be way too difficult.)
  
  vertices = []
  texcoords = []
  
  drawnw = 0
  while drawnw < bgw:
      currtilew = min(tilew, bgw - drawnw)
      currtcw   = currtilew / float(tilew)
      drawnh = 0
      while drawnh < bgh:
        L, T = l + drawnw, t + drawnh
        currtileh = min(tileh, bgh - drawnh)
        currtch   = currtileh / float(tileh)
        vertices.extend([
          (L, T + currtileh), # bottom left
          (L + currtilew, T + currtileh), # bottom right
          (L + currtilew, T), # top right
          (L, T),             # top left
        ])
        texcoords.extend([
          tc((      0, currtch), ubasis), # bottom left
          tc((currtcw, currtch), ubasis), # bottom right
          tc((currtcw,       0), ubasis), # top right
          ttl, # top left
        ])
        drawnh += currtileh
      drawnw += currtilew
  
  if action == 'evaluate':
    # typecasting them back
    return map(tuple, vertices), map(tuple, texcoords)
  
  from OpenGL import GL
  GL.glPushAttrib(GL.GL_ENABLE_BIT | GL.GL_TEXTURE_BIT | GL.GL_CURRENT_BIT)
  GL.glEnable(texture.target)
  GL.glBindTexture(texture.target, texture.id)
  GL.glBegin(GL.GL_QUADS)
  for vertex, texcoord in zip(vertices, texcoords):
    GL.glTexCoord2fv(texcoord)
    GL.glVertex2fv(vertex)
  GL.glEnd()
  GL.glPopAttrib()
  
  
  