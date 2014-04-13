from OpenGL import GL
# pyglet
import pyglet
# gui
from . import GUINode
# css
from css.color import Color


class Caret(GUINode):
  def __init__(self):
    super(Caret, self).__init__()
    self.__glyph = None
  
  @property
  def glyph(self):
    if self.__glyph is None:
      self.__glyph = self.parent.font.get_glyphs('|')[0]
    return self.__glyph
  
  def get_content_size(self):
    return (self.glyph.width, self.glyph.height)
  
  def draw(self, *args, **kwargs):
    GL.glPushMatrix()
    self.transform()
    self.glyph.draw()
    GL.glPopMatrix()


class TextEdit(GUINode):
  def __init__(self, *args, **kwargs):
    super(TextEdit, self).__init__()
    self.text_label = pyglet.text.Label(*args, **kwargs)
    self.text_objects = [self.text_label]
    self.__selection = [0, 0]
    self.update_glyphs()
    self.caret = Caret()
    self.add(self.caret)
  
  ## utility functions ##
  @property
  def font(self):
    return self.text_label.document.get_font()
  
  @property
  def text(self):
    return self.text_label.text
  
  @property
  def selection(self):
    return tuple(self.__selection)
  
  def update_glyphs(self):
    self.glyphs = self.font.get_glyphs(self.text)
    self.offsets = []
    curr_offset = 0
    for glyph in self.glyphs:
      self.offsets.append(curr_offset)
      curr_offset += glyph.advance
    self.offsets.append(curr_offset)
  
  def update_caret(self):
    sel_left, sel_right = self.__selection
    if sel_left == sel_right:
      self.caret.x = self.content_box[0] + self.offsets[sel_left]
    else:
      self.caret.x = self.content_box[0] # TODO hide at all
    self.caret.x -= self.caret.glyph.advance // 3 + 1
    self.caret.y = self.content_box[1]
  
  def get_caret_pos(self, x):
    for i, offset in enumerate(self.offsets):
      if x < offset:
        return max(0, i - 1)
    return len(self.glyphs)
  
  def apply_style(self, **options):
    super(TextEdit, self).apply_style(**options)
    tl = self.text_label
    tl.x, tl.y, tl.width, tl.height = self.content_box
    self.update_caret()
  
  def draw(self, *args, **kwargs):
    super(TextEdit, self).draw(*args, **kwargs)
    GL.glPushMatrix()
    GL.glPushAttrib(GL.GL_SCISSOR_BIT)
    self.transform()
    GL.glEnable(GL.GL_SCISSOR_TEST) # TODO move this to style['overflow'] = 'hidden'
    left, bottom = map(int, self.point_to_world(self.padding_box[:2]))
    GL.glScissor(left, bottom, *self.padding_box[2:])
    self.text_label.draw()
    GL.glPopAttrib()
    GL.glPopMatrix()
  
  ## event handlers ##
  def on_key_press(self, key, modifiers):
    print key
  
  def mouse_press(self, x, y, button, modifiers):
    x, y = self.point_to_local((x, y))
    x = x - self.content_box[0]
    # TODO handle Shift button here
    curr_caret_pos = self.get_caret_pos(x)
    new_selection = [curr_caret_pos] * 2
    old_selection = self.__selection
    self.__selection = new_selection
    self.__selection_focus = curr_caret_pos
    super(TextEdit, self).mouse_press(x, y, button, modifiers)
    self.selection_change(old_selection, new_selection)
  
  def mouse_drag(self, x, y, dx, dy, button, modifiers):
    x, y = self.point_to_local((x, y))
    x = x - self.content_box[0]
    curr_caret_pos = self.get_caret_pos(x)
    sel_focus = self.__selection_focus
    new_selection = sorted([sel_focus, curr_caret_pos])
    old_selection = self.__selection
    self.__selection = new_selection
    print "EDITOR: SELECTION:", self.__selection
    super(TextEdit, self).mouse_motion(x, y, dx, dy)
    self.selection_change(old_selection, new_selection)
  
  def mouse_release(self, x, y, button, modifiers):
    self.__selection_focus = None
    super(TextEdit, self).mouse_release(x, y, button, modifiers)
  
  def selection_change(self, old_selection, new_selection):
    if old_selection != new_selection:
      self.update_caret()
      self.dispatch_event('on_selection_change', old_selection, new_selection)


TextEdit.register_event_type('on_selection_change')

#TextEdit.style['color'] = 'red'
TextEdit.style['padding-bottom'] = 4
TextEdit.style['border'] = (2, 'inset', 'gray')
TextEdit.style['background-color'] = 'gray'
TextEdit.pseudostyle('focus')['background-color'] = 'lightgray'
TextEdit.pseudostyle('hover')['background-color'] = 'darkgray'