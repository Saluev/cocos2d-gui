# built-in
import weakref
# PyOpenGL
from OpenGL import GL, GLU
# pyglet
import pyglet
# cocos2d
import cocos
from cocos.director import director
from common.utility import reverse

# TODO change lists under cursor to recursion over ONE
# highest item under cursor' parents.

def _recursive_event(what, *args):
  """This is a private utility function that runs
  event handling recursively for all ancestors of
  SmartNode being also a SmartNode.
  
  Call example:
  
  >>> _recursive_event(self.mouse_motion, x, y, ...)
  
  So, it gets not an object, but it's bounded method
  (which provides complete information on the object
  and the method.)
  """
  obj = what.im_self
  fname = what.im_func.__name__
  while isinstance(obj, SmartNode):
    if getattr(obj, fname)(*args) == False:
      # event handling stops when someone returns False
      # (at least in JavaScript.)
      return
    obj = obj.parent


class SmartNode(pyglet.event.EventDispatcher):
  nodes_by_id = weakref.WeakValueDictionary()
  
  def __init__(self, *args, **kwargs):
    type(self).nodes_by_id[id(self)] = self
    self.nodes = []
    self.parent = None
    self.position = (0, 0)
  
  def point_to_local(self, xy):
    x, y = xy
    parent = self
    while parent is not None:
      px, py = parent.position
      x -= px
      y -= py
      parent = parent.parent
    return x, y
  
  def point_to_world(self, xy):
    x, y = xy
    parent = self
    while parent is not None:
      px, py = parent.position
      x += px
      y += py
      parent = parent.parent
    return x, y
  
  def add(self, what):
    self.nodes.append(what)
    what.parent = self # TODO weakref property
  
  def get_nodes(self):
    return self.nodes
  
  def transform(self):
    x, y = self.position
    GL.glTranslate(x, y, 0)
    pass # DEPRECATED
    #super(SmartNode, self).transform()
  
  def before_visit(self):
    GL.glPushName(id(self))
    GL.glPushMatrix()
    self.transform()
  
  def after_visit(self):
    GL.glPopName(id(self))
    GL.glPopMatrix()
  
  def smart_visit(self):
    self.draw()
    for node in self.nodes:
      node.visit()
  
  def visit(self):
    self.before_visit()
    self.smart_visit()
    self.after_visit()
  
  def before_draw(self):
    pass
  
  def after_draw(self):
    pass
  
  def smart_draw(self):
    pass # abstract
  
  def draw(self, *args, **kwargs):
    self.before_draw()
    self.smart_draw()
    self.after_draw()
  
  # shortcuts for events #
  def focus(self):
    self.dispatch_event('on_focus')
  
  def blur(self):
    self.dispatch_event('on_blur')
  
  def mouse_enter(self):
    self.dispatch_event('on_mouse_enter')
  
  def mouse_out(self):
    self.dispatch_event('on_mouse_out')
  
  def mouse_motion(self, *args):
    self.dispatch_event('on_mouse_motion', *args)
  
  def mouse_drag(self, *args):
    self.dispatch_event('on_mouse_drag', *args)
  
  def mouse_press(self, *args):
    self.dispatch_event('on_mouse_press', *args)
  
  def mouse_release(self, *args):
    self.dispatch_event('on_mouse_release', *args)
  
  def key_press(self, *args):
    self.dispatch_event('on_key_press', *args)
  
  def key_release(self, *args):
    self.dispatch_event('on_key_release', *args)


SmartNode.register_event_type('on_mouse_release')
SmartNode.register_event_type('on_mouse_motion')
SmartNode.register_event_type('on_mouse_press')
SmartNode.register_event_type('on_mouse_enter')
SmartNode.register_event_type('on_mouse_drag')
SmartNode.register_event_type('on_mouse_out')
SmartNode.register_event_type('on_key_release')
SmartNode.register_event_type('on_key_press')
SmartNode.register_event_type('on_focus')
SmartNode.register_event_type('on_blur')


class SmartLayer(cocos.layer.base_layers.Layer):
  
  is_event_handler = True
  
  def __init__(self, *args, **kwargs):
    super(SmartLayer, self).__init__(*args, **kwargs)
    self.focused = None
    self.highlighted = []
    self.__mouse_position = (-1, -1)
  
  def on_enter(self):
    director.window.push_handlers(self)
  
  def visit(self):
    self.objects_under_cursor(*self.__mouse_position)
    for child in self.get_children():
      child.visit()
  
  def objects_under_cursor(self, x, y):
    """Writes to `self.highlighted` list of
    objects under cursor, in descending order
    (the first is the top element).
    """
    if not self.children:
      return []
    
    # TODO simple rectangular check to improve performance
    viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
    GL.glSelectBuffer(512)
    GL.glRenderMode(GL.GL_SELECT)
    GL.glInitNames()
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPushMatrix()
    # copying projection
    # WARNING this approach can be unstable!
    M = GL.glGetFloatv(GL.GL_PROJECTION_MATRIX)
    GL.glLoadIdentity()
    GLU.gluPickMatrix(x, y, 1., 1., viewport)
    GL.glMultMatrixf(M)
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    super(SmartLayer, self).visit()
    
    hits = GL.glRenderMode(GL.GL_RENDER)
    result = []
    for near, far, names in hits:
      result = [] # XXX we just wish to get last hit record.
      for name in names:
        obj = SmartNode.nodes_by_id.get(name)
        if obj is not None:
          result.append(obj)
    
    GL.glMatrixMode(GL.GL_PROJECTION)
    GL.glPopMatrix()
    GL.glMatrixMode(GL.GL_MODELVIEW)
    
    old_result = self.highlighted
    new_result = list(result)
    self.highlighted = new_result
    for obj in set(old_result) - set(new_result):
      obj.mouse_out()
    for obj in set(new_result) - set(old_result):
      obj.mouse_enter()
    
    self.highlighted.reverse()
    
  
  def on_mouse_motion(self, x, y, dx, dy):
    self.__mouse_position = (x, y)
    for obj in self.highlighted[:1]:
      _recursive_event(obj.mouse_motion, x, y, dx, dy)
  
  def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
    self.__mouse_position = (x, y)
    for obj in self.highlighted[:1]:
      _recursive_event(obj.mouse_drag, x, y, dx, dy, button, modifiers)
  
  def on_mouse_press(self, x, y, button, modifiers):
    self.__mouse_position = (x, y)
    old_focused = self.focused
    new_focused = (self.highlighted or [None])[0]
    if old_focused != new_focused:
      # blurring previously focused object
      # TODO undo on False
      if old_focused is not None:
        old_focused.blur()
      # focusing newly focused object
      if new_focused is not None:
        new_focused.focus()
    self.focused = new_focused
    # pressing
    for obj in self.highlighted[:1]:
      _recursive_event(obj.mouse_press, x, y, button, modifiers)
    if self.highlighted:
      return True
  
  def on_mouse_release(self, x, y, button, modifiers):
    self.__mouse_position = (x, y)
    for obj in self.highlighted[:1]:
      _recursive_event(obj.mouse_release, x, y, button, modifiers)
    if self.highlighted:
      return True
  
  def on_key_press(self, key, modifiers):
    if self.focused is not None:
      self.focused.key_press(key, modifiers)
      return True
  
  def on_key_release(self, key, modifiers):
    if self.focused is not None:
      self.focused.key_release(key, modifiers)
      return True

