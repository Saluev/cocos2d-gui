# OpenGL
from OpenGL import GL
# pyglet
import pyglet
# gui
from .node import GUINode


class Button(GUINode):
  def __init__(self, *args, **kwargs):
    super(Button, self).__init__()
    self.text_label = pyglet.text.Label(*args, **kwargs)
    self.text_objects = (self.text_label,)
  
  def __repr__(self):
    return '<cocosgui.buttons.Button \'%s\' at %s>' % (self.text, hex(id(self)))
  
  def draw(self, *args, **kwargs):
    super(Button, self).draw(*args, **kwargs)
    GL.glPushMatrix()
    self.transform()
    self.text_label.draw()
    GL.glPopMatrix()
  
  def apply_style(self, **options):
    super(Button, self).apply_style(**options)
    tl = self.text_label
    tl.x, tl.y, tl.width, tl.height = self.content_box
  
  @property
  def text(self):
    return self.text_label.text
  
  @text.setter
  def text(self, value):
    self.text_label.text = value


Button.register_event_type('on_click')

Button.style.update({
  'width': 100,
  'height': 14,
  'padding': 4,
  'border': (2, 'outset', '#AAA'),
  'background-color': '#AAA',
})
Button.pseudostyle('hover').update({
  'border': (2, 'outset', '#DDD'),
  'background-color': '#DDD',
})
Button.pseudostyle('active').update({
  'border': (2, 'inset', '#DDD'),
  'background-color': '#DDD',
})
