# OpenGL
from OpenGL import GL
# pyglet
import pyglet
# gui
from . import CSSNode, GUINode

class Button(GUINode):
  def __init__(self, *args, **kwargs):
    super(Button, self).__init__()
    self.text_label = pyglet.text.Label(*args, **kwargs)
    
  #def get_content_size(self):
    #element = self.text_layer.element
    #return element.width, element.height
  
  def draw(self, *args, **kwargs):
    GL.glPushMatrix()
    self.transform()
    self.text_label.draw()
    GL.glPopMatrix()
  
  @property
  def text(self):
    return self.text_layer.element.text
  
  @text.setter
  def text(self, value):
    self.text_layer.element.text = value
