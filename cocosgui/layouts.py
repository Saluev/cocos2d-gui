from .node import GUINode


class GUILayout(GUINode):
  def __init__(self, spacing=5):
    super(GUILayout, self).__init__()
    self.spacing = spacing
    self.__nodes = [] # TODO move this whole system to GUINode
  
  def __len__(self):
    return len(self.children)
  
  def get_children(self):
    return self.__nodes
  
  def add(self, child, *args, **kwargs):
    super(GUILayout, self).add(child, *args, **kwargs)
    self.__nodes.append(child)
    nodes = self.get_nodes()
    nodes_count = len(nodes)
    for i, node in enumerate(nodes):
      if i == 0:
        node.add_state('first-child')
      else:
        node.remove_state('first-child')
      if i == nodes_count - 1:
        node.add_state('last-child')
      else:
        node.remove_state('last-child')


class VerticalLayout(GUILayout):
  
  def get_content_size(self):
    children = self.get_children()
    if not children:
      return (0, 0)
    child_widths  = (child.width  for child in children)
    child_heights = (child.height for child in children)
    width  = max(child_widths )
    height = sum(child_heights) + self.spacing * (len(children) - 1)
    return (width, height)
  
  def apply_style(self, **options):
    super(VerticalLayout, self).apply_style(**options)
    # now place children properly
    children = self.get_children()[::-1]
    xoffset, yoffset = self.content_box[:2]
    for child in children:
      box = child.margin_box
      child.set_position(xoffset, yoffset)
      yoffset += box[3]
      yoffset += self.spacing


class HorizontalLayout(GUILayout):
  
  def get_content_size(self):
    children = self.get_children()
    if not children:
      return (0, 0)
    child_widths  = (child.width  for child in children)
    child_heights = (child.height for child in children)
    width  = sum(child_widths ) + self.spacing * (len(children) - 1)
    height = max(child_heights)
    return (width, height)
  
  def apply_style(self, **options):
    super(HorizontalLayout, self).apply_style(**options)
    # now place children properly
    children = self.get_children()
    xoffset, yoffset = self.content_box[:2]
    for child in children:
      box = child.margin_box
      child.set_position(xoffset, yoffset)
      xoffset += box[2]
      xoffset += self.spacing
