from OpenGL import GL
from cocos.director import director
from .node import GUINode


def _anchor_to_position_a(anchor, window_size, self_size):
  abs_anchor = abs(anchor)
  if isinstance(abs_anchor, int):
    result = abs_anchor
  elif isinstance(abs_anchor, float):
    result = int(window_size * abs_anchor)
  # TODO px, em, etc.?
  if anchor < 0:
    result = window_size - result - self_size
  return result

def _anchor_to_position_c(anchor, window_size, self_size):
  abs_anchor = abs(anchor)
  if isinstance(abs_anchor, int):
    result = abs_anchor
  elif isinstance(abs_anchor, float):
    result = int(window_size * abs_anchor * 0.01) - self_size // 2
  # TODO px, em, etc.?
  if anchor < 0:
    result = window_size - result - self_size
  return result


class AttachedWindow(GUINode):
  
  def __init__(self, attach=None, **kwargs):
    super(AttachedWindow, self).__init__(**kwargs)
    self.attach = attach
  
  def get_content_size(self):
    nodes = self.get_nodes()
    if not nodes:
      return (0, 0)
    else:
      return nodes[0].width, nodes[0].height
  
  def evaluate_position(self):
    if self.attach is not None:
      ww, wh = director.window.width, director.window.height
      sw, sh = self.margin_box[2:4]
      anchor_x, anchor_y = self.attach
      x = _anchor_to_position_a(anchor_x, ww, sw)
      y = _anchor_to_position_a(anchor_y, wh, sh)
      self.position = (x, y)
  
  def visit(self):
    self.evaluate_position()
    super(AttachedWindow, self).visit()
  
  #def add(self, child, *args, **kwargs):
    #if len(self.get_children()) >= 1:
      #raise RuntimeError(
        #'Only one child is supported for %s. '
        #'Use layouts to add more objects.' % type(self).__name__)
    #super(AttachedWindow, self).add(child, *args, **kwargs)


class CenteredWindow(AttachedWindow):
  
  def evaluate_position(self):
    if self.attach is not None:
      ww, wh = director.window.width, director.window.height
      sw, sh = self.margin_box[2:4]
      anchor_x, anchor_y = self.attach
      x = _anchor_to_position_c(anchor_x, ww, sw)
      y = _anchor_to_position_c(anchor_y, wh, sh)
      self.position = (x, y)


class ModalWindow(CenteredWindow):
  def __init__(self, attach=(50., 50.), fade_color=(0, 0, 0, 128), **kwargs):
    super(ModalWindow, self).__init__(attach=attach, **kwargs)
    self.fade_color = fade_color
  
  def apply_style(self, **options):
    super(ModalWindow, self).apply_style(**options)
    self.z = 777
  
  def draw(self):
    ww, wh = 2000, 2000
    GL.glPushMatrix()
    self.transform()
    GL.glPushAttrib(GL.GL_CURRENT_BIT)
    GL.glBegin(GL.GL_QUADS)
    GL.glColor4ubv(self.fade_color)
    map(GL.glVertex2fv, [(-ww, -wh), (ww, -wh), (ww, wh), (-ww, wh)])
    GL.glEnd()
    GL.glPopAttrib()
    GL.glPopMatrix()
    super(ModalWindow, self).draw()
  
  def on_mouse_press(self, x, y, button, modifiers):
    pass # TODO close itself
    return False
  
  def on_mouse_motion(self, *args):
    return False

