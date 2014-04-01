# cocos2D
import cocos.sprite
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


class GUIImage(GUINode):
  def __init__(self, image, style = None):
    super(GUIImage, self).__init__(style)
    self.image = image
    self.add(cocos.sprite.Sprite(image, anchor=(0,0)))
  
  def get_content_size(self):
    return (self.image.width, self.image.height)


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


# a simple test
from ..resources import get as resources_get
from .layouts import VerticalLayout
window = GUIWindow()
layout = VerticalLayout()
img = resources_get('grassland')
layout.add(GUIImage(img))
layout.add(GUIImage(img))
window.add(layout)
window.order()