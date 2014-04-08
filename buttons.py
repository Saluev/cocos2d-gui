# cocos2d
import cocos
# gui
from . import CSSNode, GUINode

class Button(GUINode):
  def __init__(self, *args, **kwargs):
    super(Button, self).__init__()
    self.__text = text
    self.text_layer = cocos.text.Label(*args, **kwargs)
    self.add(self.text_layer)
    
  #def get_content_size(self):
    #element = self.text_layer.element
    #return element.width, element.height
  
  @property
  def text(self):
    return self.__text
  
  @text.setter
  def text(self, value):
    self.__text = value
    self.text_layer.element.text = value
