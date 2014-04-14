# PyOpenGL
try:
  from OpenGL import GL
except ImportError:
  from logging import warn
  warn('Couldn\'t import PyOpenGL.')
# cocos2d
from cocos.director import director
# css
import border, borderimage, background, style
from .utility import expand_sided_value, expand_hv_value
from .color import Color
import texturing
from .texturing import rect_from_sides


class BorderSide(border.BorderSide):
  def apply_to(self, node):
    super(BorderSide, self).apply_to(node)
    self.__prepare()
  
  ## drawing functions ##
  def __prepare(self):
    node = self.node
    border_box = node.border_box
    border = node.evaluated_style.border
    width, style, color = self.width, self.style, Color(self.color)
    if width <= 0 or \
       style in ('none', 'hidden') or \
       color.is_transparent():
      self.__vertices = []
      return
    if self.style not in ('solid', 'hidden', 'inset', 'outset'):
      raise NotImplementedError(
        "%s border style is not yet "
        "implemented" % self.style.title()
      )
    x, y, w, h = border_box
    l, t, r, b = x, y, x + w, y + h
    side = self.prefix
    if side == 'left':
      vertices = [(l, t), (l, b), 
        (l + width, b - border.bottom.width),
        (l + width, t + border.top   .width)]
    elif side == 'right':
      vertices = [(r, t), (r, b),
        (r - width, b - border.bottom.width),
        (r - width, t + border.top   .width)]
    elif side == 'bottom':
      vertices = [(l, t), (r, t),
        (r - border.right.width, t + width),
        (l + border.left .width, t + width)]
    elif side == 'top':
      vertices = [(l, b), (r, b),
        (r - border.right.width, b - width),
        (l + border.left .width, b - width)]
    else:
      assert False, '`BorderSide` class seems to be invalid.'
    self.__color = color
    # lightening or darkening color if inset or outset
    if (style, side) in [('inset',  'left' ), ('inset',  'top'   ),
                         ('outset', 'right'), ('outset', 'bottom')]:
      self.__color = color.darken()
    if (style, side) in [('inset',  'right'), ('inset',  'bottom'),
                         ('outset', 'left' ), ('outset', 'top'   )]:
      self.__color = color.lighten()
    self.__vertices_count = len(vertices)
    self.__vertices = texturing.to_buffer(vertices)
  
  def _Border__draw(self):
    if not self.__vertices:
      return
    
    GL.glPushAttrib(GL.GL_CURRENT_BIT | GL.GL_ENABLE_BIT)
    GL.glPushClientAttrib(GL.GL_CLIENT_ALL_ATTRIB_BITS)
    
    GL.glColor4ubv(self.__color)
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, self.__vertices)
    GL.glDrawArrays(GL.GL_QUADS, 0, self.__vertices_count)
    
    GL.glPopClientAttrib()
    GL.glPopAttrib()


class BorderImage(borderimage.BorderImage):
  def apply_to(self, node):
    super(BorderImage, self).apply_to(node)
    self.__prepare()
  
  ## drawing functions ##
  def __prepare(self):
    if self.source == 'none':
      return
    
    node = self.node
    
    box = node.border_box
    left, top, box_width, box_height = box
    right, bottom = left + box_width, top + box_height
    
    image = self.source
    repeat = expand_hv_value(self.repeat)
    width = self.__evaluate_image_width(node)
    slice = self.__evaluate_image_slice(node)
    
    fill = slice[0]
    iw, ih = image.width, image.height
    hrepeat, vrepeat = repeat
    wb, wr, wt, wl = width
    sb, sr, st, sl = map(float, slice[1:])
    
    # dimensions of the central part of an image
    scw = iw - sr - sl
    sch = ih - st - sb
    
    # sizes of large border parts (horiz. and vert. bars)
    h_bar_width  = box_width  - wl - wr
    v_bar_height = box_height - wt - wb
    
    # tile sizes
    if hrepeat == 'stretch':
      h_tile_top_width = h_tile_bottom_width = h_bar_width
    elif hrepeat == 'repeat':
      h_tile_top_width    = int(scw * (wt / st))
      h_tile_bottom_width = int(scw * (wb / sb))
    elif hrepeat == 'round':
      h_tile_width = lambda th: h_bar_width / round(h_bar_width / float(th))
      h_tile_top_width    = h_tile_width(wt)
      h_tile_bottom_width = h_tile_width(wb)
    else:
      raise ValueError(
        'Invalid value for background-image-repeat: %r' % hrepeat)
    
    if vrepeat == 'stretch':
      v_tile_left_height = v_tile_right_height = v_bar_height
    elif vrepeat == 'repeat':
      v_tile_left_height  = int(sch * (wl / sl))
      v_tile_right_height = int(sch * (wr / sr))
    elif vrepeat == 'round':
      v_tile_height = lambda tw: v_bar_height / round(v_bar_height / float(tw))
      v_tile_left_height  = v_tile_height(wl)
      v_tile_right_height = v_tile_height(wr)
    else:
      raise ValueError(
        'Invalid value for background-image-repeat: %r' % hrepeat)
    
    tiling_arguments = {
      'top-left': {
        'rect': (left, top, wl, wt),
        'tile_size': (wl, wt),
        'texcoords': rect_from_sides(
          left = 0., top = 1.,
          right = sl / iw, bottom = 1. - st / ih
        )
      },
      'top': {
        'rect': (left + wl, top, h_bar_width, wt),
        'tile_size': (h_tile_top_width, wt),
        'texcoords': rect_from_sides(
          left = sl / iw, top = 1.,
          right = 1. - sr / iw, bottom = 1 - st / ih
        )
      },
      'top-right': {
        'rect': (right - wr, top, wr, wt),
        'tile_size': (wr, wt),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = 1.,
          right = 1., bottom = 1. - st / ih
        )
      },
      'left': {
        'rect': (left, top + wt, wl, v_bar_height),
        'tile_size': (wl, v_tile_left_height),
        'texcoords': rect_from_sides(
          left = 0., top = 1. - st / ih,
          right = sl / iw, bottom = sb / ih
        )
      },
      'right': {
        'rect': (right - wr, top + wt, wr, v_bar_height),
        'tile_size': (wr, v_tile_right_height),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = 1. - st / ih,
          right = 1., bottom = sb / ih
        )
      },
      'bottom-left': {
        'rect': (left, bottom - wb, wl, wb),
        'tile_size': (wl, wb),
        'texcoords': rect_from_sides(
          left = 0., top = sb / ih,
          right = sl / iw, bottom = 0.
        )
      },
      'bottom': {
        'rect': (left + wl, bottom - wb, h_bar_width, wb),
        'tile_size': (h_tile_bottom_width, wb),
        'texcoords': rect_from_sides(
          left = sl / iw, top = sb/ ih,
          right = 1. - sr / iw, bottom = 0.
        )
      },
      'bottom-right': {
        'rect': (right - wr, bottom - wb, wr, wb),
        'tile_size': (wr, wb),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = sb / ih,
          right = 1., bottom = 0.
        )
      },
    }
    if fill:
      tiling_arguments['center'] = {
        'rect': (left + wl, top + wt, h_bar_width, v_bar_height),
         # size and height are resized like those of the
         # top and left image slices, respectively:
        'tile_size': (h_tile_top_width, v_tile_left_height),
        'texcoords': rect_from_sides(
          left = sl / iw, top = 1. - st / ih,
          right = 1. - sr / iw, bottom = sb / ih
        )
      }
    
    texture = image.get_texture()
    self.__vertices  = []
    self.__texcoords = []
    
    for kwargs in tiling_arguments.itervalues():
      v, tc = texturing.tile(texture, action='evaluate', **kwargs)
      self.__vertices.extend(v)
      self.__texcoords.extend(tc)
    
    # now optimization
    self.__vertices_count = len(self.__vertices)
    self.__vertices  = texturing.to_buffer(self.__vertices )
    self.__texcoords = texturing.to_buffer(self.__texcoords)
  
  def _Border__draw(self):
    if self.source == 'none':
      return
    
    texture = self.source.get_texture()
    
    GL.glPushAttrib(GL.GL_ENABLE_BIT | GL.GL_TEXTURE_BIT)
    GL.glPushClientAttrib(GL.GL_CLIENT_ALL_ATTRIB_BITS)
    
    GL.glEnable(texture.target)
    GL.glBindTexture(texture.target, texture.id)
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY)
    GL.glVertexPointer  (2, GL.GL_FLOAT, 0, self.__vertices )
    GL.glTexCoordPointer(2, GL.GL_FLOAT, 0, self.__texcoords)
    GL.glDrawArrays(GL.GL_QUADS, 0, self.__vertices_count)
    
    GL.glPopClientAttrib()
    GL.glPopAttrib()


class Border(border.Border):
  defaults = dict(border.Border.defaults, **{
    'left'  : lambda: BorderSide('left'  ),
    'top'   : lambda: BorderSide('top'   ),
    'right' : lambda: BorderSide('right' ),
    'bottom': lambda: BorderSide('bottom'),
    'image' : BorderImage,
  })
  
  def draw(self):
    if self.image.source != 'none':
      self.image.__draw()
    else:
      for side in (self.left, self.top, self.right, self.bottom):
        side.__draw()


style.Style.defaults['border'] = Border
_default_border = style.styles['*'].get_by_subname('border')
_default_image = _default_border.get_by_subname('image')
_default_border.set_by_subname('image', BorderImage(_default_image))
style.styles['*'].set_by_subname('border', Border(_default_border))
