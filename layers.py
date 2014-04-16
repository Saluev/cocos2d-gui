# cocos2d
from cocos.director import director
# gui
from .css import CSSNode, evaluate as css_evaluate
from .base import SmartLayer
from .node import GUINode

class GUILayer(SmartLayer, CSSNode):
  
  def __init__(self, *args, **kwargs):
    SmartLayer.__init__(self, *args, **kwargs)
    CSSNode.__init__(self)
  
  def order(self):
    css_evaluate(self)
  
  def get_nodes(self):
    return [child for child in self.get_children() if isinstance(child, GUINode)]
  
  def get_content_size(self):
    return (director.window.width, director.window.height)


class LayerContainer(GUINode):
  def get_content_size(self):
    return director.window.width, director.window.height
  
  def add(self, what):
    pass
  
  def on_enter(self):
    pass

