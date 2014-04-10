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
  
  def order(self):
    css_evaluate(self.window, self.parent)
  
  @property
  def window(self):
    parent = self.parent
    while not isinstance(parent, GUIWindow) and parent is not None:
      parent = parent.parent
    return parent
  
  def get_nodes(self):
    children = self.get_children()
    return [child for child in children if isinstance(child, CSSNode)]
  
  def draw(self, *args, **kwargs):
    super(GUINode, self).draw(*args, **kwargs)
    self.evaluated_style.background.draw(self)
    self.evaluated_style.border.draw(self)
  
  def on_mouse_enter(self):
    self.add_state('hover')
  
  def on_mouse_out(self):
    self.remove_state('hover')


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


# a simple test
from ..resources import get as resources_get
from .layouts import VerticalLayout
from .buttons import Button
from .windows import AttachedWindow
window = AttachedWindow()
layout = VerticalLayout()
layout.style['padding'] = 10
layout.style['border']  = 17, 'solid', '#000000'
layout.style['background'] = '#DDDDDD'
img1 = GUIImage(resources_get('grassland'))
img2 = GUIImage(resources_get('stone_pile_1'))
img3 = resources_get('granite_frame')
img1.style['border'] = 5, 'solid', 'green'
img1.style['background-color'] = 'darkgreen'
img1.pseudostyle('hover')['border-bottom-color'] = 'blue'
img1.style['border-style'] = 'inset'
img2.style['border'] = 5, 'outset', 'blue'
img2.style['background-color'] = 'darkblue'
layout.style['background-image'] = img1.image
#layout.style['background-size'] = 'contain'
img3.apply_to(layout)
#layout.style['border-image-source'] = img3
#layout.style['border-image-slice'] = ('fill', 17)
#layout.style['border-image-repeat'] = 'repeat'
btn = Button('Hi there!')
btn.style['width' ] = 100
btn.style['height'] = 20
layout.add(img1)
layout.add(img2)
layout.add(btn)
window.add(layout)
window.attach = (-50, -50)
window.order()