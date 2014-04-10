from cocos.director import director
from . import GUIWindow

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


class AttachedWindow(GUIWindow):
  
  def __init__(self, attach=None, *args, **kwargs):
    super(AttachedWindow, self).__init__(*args, **kwargs)
    self.attach = attach
  
  def evaluate_position(self):
    if self.attach is not None:
      ww, wh = director.window.width, director.window.height
      sw, sh = self.get_content_size()
      anchor_x, anchor_y = self.attach
      x = _anchor_to_position_a(anchor_x, ww, sw)
      y = _anchor_to_position_a(anchor_y, wh, sh)
      self.position = (x, y)
  
  def visit(self):
    self.evaluate_position()
    super(AttachedWindow, self).visit()


class CenteredWindow(AttachedWindow):
  
  def evaluate_position(self):
    if self.attach is not None:
      ww, wh = director.window.width, director.window.height
      sw, sh = self.get_content_size()
      anchor_x, anchor_y = self.attach
      x = _anchor_to_position_c(anchor_x, ww, sw)
      y = _anchor_to_position_c(anchor_y, wh, sh)
      self.position = (x, y)

