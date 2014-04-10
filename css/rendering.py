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


class BorderSide(border.BorderSide):
  def _Border__draw(self, node):
    if self.__vertices is None:
      self.__prepare(node)
    if not self.__vertices:
      return
    
    GL.glPushAttrib(GL.GL_CURRENT_BIT | GL.GL_ENABLE_BIT)
    GL.glPushClientAttrib(GL.GL_CLIENT_ALL_ATTRIB_BITS)
    
    GL.glColor3ubv(self.__color)
    GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
    GL.glVertexPointer(2, GL.GL_FLOAT, 0, self.__vertices)
    GL.glDrawArrays(GL.GL_QUADS, 0, self.__vertices_count)
    
    GL.glPopClientAttrib()
    GL.glPopAttrib()


class BorderImage(borderimage.BorderImage):
  def _Border__draw(self, node):
    if self.source == 'none':
      return
    if self.__vertices is None or self.__texcoords is None:
      # TODO check whether node is the same
      self.__prepare(node)
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
  
  def draw(self, node):
    if self.image.source != 'none':
      self.image.__draw(node)
    else:
      for side in (self.left, self.top, self.right, self.bottom):
        side.__draw(node)


style.Style.defaults['border'] = Border
_default_border = style.styles['*'].get_by_subname('border')
_default_image = _default_border.get_by_subname('image')
_default_border.set_by_subname('image', BorderImage(_default_image))
style.styles['*'].set_by_subname('border', Border(_default_border))
