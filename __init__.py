# PyOpenGL
from OpenGL import GL
# cocos2D
import cocos.director, cocos.sprite
# client
from .. import SmartNode, SmartLayer
from .css import Style, CSSNode, evaluate as css_evaluate


class GUINode(SmartNode, CSSNode):
  def __init__(self, style = None):
    SmartNode.__init__(self)
    CSSNode.__init__(self, style)
    self.anchor = (0, 0)
  
  def get_nodes(self):
    children = self.get_children()
    return [child for child in children if isinstance(child, CSSNode)]
  
  def draw(self, *args, **kwargs):
    super(GUINode, self).draw(*args, **kwargs)
    self.style.border.draw(self)
    self.style.background.draw(self)


class GUIImage(GUINode):
  def __init__(self, image, style = None):
    super(GUIImage, self).__init__(style)
    self.image = image
    self.sprite = cocos.sprite.Sprite(image, anchor=(0,0))
    self.add(self.sprite)
  
  def get_content_size(self):
    return (self.image.width, self.image.height)
  
  def visit(self):
    # TODO transform coordinates or draw image manually
    cx, cy = self.content_box[:2]
    sx, sy = self.position
    self.sprite.position = (cx - sx, cy - sy)
    super(GUIImage, self).visit()


class GUIWindow(SmartLayer, CSSNode):
  
  is_event_handler = True
  
  def __init__(self, *args, **kwargs):
    SmartLayer.__init__(self, *args, **kwargs)
    CSSNode.__init__(self)
  
  def order(self):
    css_evaluate(self)
  
  def add(self, child, *args, **kwargs):
    if len(self.get_children()) > 1:
      raise RuntimeError(
        'Only one child is supported for GUIWindow. '
        'Use layouts to add more objects.'
      )
    SmartLayer.add(self, child, *args, **kwargs)
  
  def get_nodes(self):
    return self.get_children()[:1]
  
  def get_content_size(self):
    child = self.get_children()[0]
    return (child.width, child.height)
  
  def visit(self):
    GL.glPushMatrix()
    GL.glTranslatef(0, cocos.director.director.window.height, 0)
    GL.glScalef(1, -1, 1)
    super(GUIWindow, self).visit()
    GL.glPopMatrix()


