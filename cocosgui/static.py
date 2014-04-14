import cocos
from .node import GUINode

class Image(GUINode): # TODO: call it just Image
  def __init__(self, image, style = None):
    super(Image, self).__init__(style)
    self.image = image
    self.sprite = cocos.sprite.Sprite(image, anchor=(0,0))
    self.add(self.sprite)
  
  def get_content_size(self):
    return (self.image.width, self.image.height)
  
  def apply_style(self, **options):
    super(Image, self).apply_style(**options)
    self.sprite.position = self.content_box[:2]


class Label(GUINode):
  def __init__(self, style = None, *args, **kwargs):
    super(Label, self).__init__(style)
    self.label = cocos.text.Label(*args, **kwargs)
    self.add(self.label)
  
  def apply_style(self, **options):
    super(Label, self).apply_style(**options)
    self.label.position = self.content_box[:2]

