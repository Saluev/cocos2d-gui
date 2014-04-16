from OpenGL import GL
import pyglet
import cocos
from .node import GUINode

class Image(GUINode): # TODO: call it just Image
  def __init__(self, image):
    super(Image, self).__init__()
    self.image = image
    self.sprite = cocos.sprite.Sprite(image, anchor=(0,0))
    #self.add(self.sprite)
  
  def smart_draw(self):
    self.sprite.draw()
  
  def get_content_size(self):
    return (self.image.width, self.image.height)
  
  def apply_style(self, **options):
    super(Image, self).apply_style(**options)
    self.sprite.position = self.content_box[:2]


class Label(GUINode):
  def __init__(self, *args, **kwargs):
    super(Label, self).__init__()
    self.text_label = pyglet.text.Label(*args, **kwargs)
    self.text_objects = (self.text_label,)
  
  def get_content_size(self):
    font = self.text_label.document.get_font()
    glyphs = font.get_glyphs(self.text_label.text)
    width  = sum(glyph.advance for glyph in glyphs)
    height = max(glyph.height  for glyph in glyphs)
    return (width, height)
  
  def apply_style(self, **options):
    super(Label, self).apply_style(**options)
    tl = self.text_label
    tl.x, tl.y, tl.width, tl.height = self.content_box

  def smart_draw(self):
    super(Label, self).smart_draw()
    self.text_label.draw()
