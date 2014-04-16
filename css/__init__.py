__all__ = [
  'styles', 'Style', 'CSSNode',
  'evaluate'
]

# importing basic names to publish them
from .style import styles, Style
from .node import CSSNode
# importing extensions
import border, borderimage, background, font
import rendering

def evaluate(window, element = None):
  if window is None:
    return
  if element is None:
    element = window
  element.evaluate_style()
  children = element.get_nodes()
  for child in children:
    assert(child.parent is element)
    evaluate(window, child)
  _evaluate_node(element)

def _evaluate_node(node):
  parent, style = node.parent, node.evaluated_style
  left, bottom = style['left'], style['top']
  left   = 0 if left   == 'auto' else left
  bottom = 0 if bottom == 'auto' else bottom
  position = style['position']
  if position == 'absolute':
    raise NotImplementedError
  # TODO fixed?
  margin_offset  = [left, bottom]
  border_offset  = [margin_offset[0] + style['margin-left'],
                    margin_offset[1] + style['margin-bottom' ]]
  padding_offset = [border_offset[0] + style['border-left-width'],
                    border_offset[1] + style['border-bottom-width' ]]
  content_offset = [padding_offset[0] + style['padding-left'],
                    padding_offset[1] + style['padding-bottom' ]]
  content_box = content_offset + list(node.get_content_size())
  assert(all(isinstance(val, int) for val in content_box))
  padding_box = padding_offset + [sum((
    content_box[2],
    style['padding-left'  ],
    style['padding-right' ],
  )), sum((
    content_box[3],
    style['padding-top'   ],
    style['padding-bottom'],
  ))]
  border_box = border_offset + [sum((
    padding_box[2],
    style['border-left-width'  ],
    style['border-right-width' ],
  )), sum((
    padding_box[3],
    style['border-top-width'   ],
    style['border-bottom-width'],
  ))]
  margin_box = margin_offset + [sum((
    border_box[2],
    style['margin-left'  ],
    style['margin-right' ],
  )), sum((
    border_box[3],
    style['margin-top'   ],
    style['margin-bottom'],
  ))]
  #width, height = style['width'], style['height'] # TODO percentages?
  #width  = margin_box[2] if width  == 'auto' else width
  #height = margin_box[3] if height == 'auto' else height
  #dw, dh = width - margin_box[2], height - margin_box[3]
  #if dw != 0 or dh != 0:
    #for box in [margin_box, border_box, padding_box, content_box]:
      #box[2] += dw
      #box[3] += dh
  info = {
    'node': node,
    'margin_box' : margin_box,
    'border_box' : border_box,
    'padding_box': padding_box,
    'content_box': content_box,
  }
  node.apply_style(**info)
