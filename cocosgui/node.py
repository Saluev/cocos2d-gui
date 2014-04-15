from OpenGL import GL
from .css import CSSNode, evaluate as css_evaluate
from .base import SmartNode


class GUINode(SmartNode, CSSNode):
  def __init__(self, style = None):
    SmartNode.__init__(self)
    CSSNode.__init__(self, style)
    self.anchor = (0, 0)
  
  def order(self):
    css_evaluate(self.window, self.parent)
  
  @property
  def z(self):
    siblings = self.parent.children
    zvalues, siblings = zip(*siblings)
    return zvalues[siblings.index(self)]
  
  @z.setter
  def z(self, value):
    siblings = self.parent.children
    zvalues, siblings = map(list, zip(*siblings))
    zvalues[siblings.index(self)] = value
    self.parent.children = sorted(zip(zvalues, siblings))
  
  @property
  def window(self):
    from .layers import GUILayer
    parent = self.parent
    while not isinstance(parent, GUILayer) and parent is not None:
      parent = parent.parent
    return parent
  
  def get_nodes(self):
    children = self.get_children()
    return [child for child in children if isinstance(child, CSSNode)]
  
  def draw(self, *args, **kwargs):
    super(GUINode, self).draw(*args, **kwargs)
    GL.glPushMatrix()
    self.transform()
    self.evaluated_style.background.draw()
    self.evaluated_style.border.draw()
    GL.glPopMatrix()
  
  def focus(self):
    self.add_state('focus')
    super(GUINode, self).focus()
  
  def blur(self):
    self.remove_state('focus')
    super(GUINode, self).blur()
  
  def mouse_enter(self):
    self.add_state('hover')
    super(GUINode, self).mouse_enter()
  
  def mouse_out(self):
    self.remove_state('hover')
    super(GUINode, self).mouse_out()
  
  def mouse_press(self, *args):
    self.add_state('active')
    super(GUINode, self).mouse_press(*args)
  
  def mouse_release(self, *args):
    self.remove_state('active')
    super(GUINode, self).mouse_release(*args)

