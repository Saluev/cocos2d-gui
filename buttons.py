# OpenGL
from OpenGL import GL
# pyglet
import pyglet
# gui
from . import GUINode

class Button(GUINode):
  def __init__(self, *args, **kwargs):
    super(Button, self).__init__()
    self.text_label = pyglet.text.Label(*args, **kwargs)
  
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
