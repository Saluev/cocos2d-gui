from . import GUINode


class GUILayout(GUINode):
  def __init__(self, spacing=5):
    super(GUILayout, self).__init__()
    self.spacing = spacing
  
  def __len__(self):
    return len(self.children)
  
  def add(self, child, *args, **kwargs):
    super(GUILayout, self).add(child, *args, **kwargs)


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
    children = self.get_children()
    xoffset, yoffset = self.content_box[:2]
    for child in children:
      box = child.margin_box
      child.set_position(xoffset, yoffset)
      yoffset += box[3]
      yoffset += self.spacing

