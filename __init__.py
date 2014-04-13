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


class GUIImage(GUINode): # TODO: call it just Image
  def __init__(self, image, style = None):
    super(GUIImage, self).__init__(style)
    self.image = image
    self.sprite = cocos.sprite.Sprite(image, anchor=(0,0))
    self.add(self.sprite)
  
  def get_content_size(self):
    return (self.image.width, self.image.height)
  
  def apply_style(self, **options):
    super(GUIImage, self).apply_style(**options)
    self.sprite.position = self.content_box[:2]


class Label(GUINode):
  def __init__(self, style = None, *args, **kwargs):
    super(Label, self).__init__(style)
    self.label = cocos.text.Label(*args, **kwargs)
    self.add(self.label)
  
  def apply_style(self, **options):
    super(Label, self).apply_style(**options)
    self.label.position = self.content_box[:2]


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
#"""
from ..resources import get as resources_get
from .layouts import VerticalLayout
from .buttons import Button
from .editors import TextEdit
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
#GUIImage.pseudostyle('hover')['border-bottom'] = (5, 'solid', 'blue')
img1.pseudostyle('focus')['border-right-color'] = 'cyan'
img1.pseudostyle('active')['border-left-color'] = 'magenta'
img1.pseudostyle('hover')['border-top-color'] = 'red'
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
btn.style['height'] = 16
edt = TextEdit(text='yoptayoptayoptayoptayopta')
edt.style['width'] = 100
edt.style['height'] = 16
layout.add(img1)
layout.add(img2)
layout.add(btn)
layout.add(edt)
window.add(layout)
window.attach = (-50, -50)
window.order()#"""