
from .utility import expand_sided_value, expand_hv_value
from .style import styles, StylesContainer
from . import texturing
from .texturing import rect_from_sides


class BorderImage(StylesContainer):
  prefix = 'image'
  subnames = [
    'source', 'slice', 'width', 'outset', 'repeat'
  ]
  
  # TODO get_as_value, set_to_value
  
  def __init__(self, *args, **kwargs):
    super(BorderImage, self).__init__(*args, **kwargs)
    self.__vertices  = None
    self.__texcoords = None
  
  def __get_image_width(self):
    return expand_sided_value(self.width)
  
  def __get_image_slice(self):
    slice = self.slice
    if isinstance(slice, (tuple, list)) and 'fill' in slice:
      slice = filter(lambda s: s != 'fill', slice) # removing 'fill'
      return (True, ) + expand_sided_value(slice)
    else:
      return (False,) + expand_sided_value(slice)
  
  def __evaluate_image_width(self, node):
    # see developer.mozilla.org/en-US/docs/Web/CSS/border-image-width
    image_width = self.__get_image_width()
    border_width = expand_sided_value(node.evaluated_style['border-width'])
    def evaluate_width(iw, bw):
      if isinstance(iw, int):      # ratio
        return iw * bw
      elif isinstance(iw, float):  # percentage
        return int(iw * bw / 100.)
      else:                        # length (px, em, etc.)
        # TODO TODO handle pixel lengths separately
        raise NotImplementedError
    width = map(evaluate_width, image_width, border_width)
    return width
  
  def __evaluate_image_slice(self, node):
    # see developer.mozilla.org/en-US/docs/Web/CSS/border-image-slice
    # TODO implement `fill` keyword
    assert(self.source != 'none')
    image = self.source
    image_slice = self.__get_image_slice()
    fill, image_slice = image_slice[0], image_slice[1:]
    def evaluate_slice(sl, image_size):
      if isinstance(sl, float):
        return min(image_size, int(image_size * sl / 100.))
      elif isinstance(sl, int):
        return min(image_size, sl)
      raise ValueError
    slice = [ fill,
      evaluate_slice(image_slice[0], image.height), # top
      evaluate_slice(image_slice[1], image.width ), # right
      evaluate_slice(image_slice[2], image.height), # bottom
      evaluate_slice(image_slice[3], image.width ), # left
    ]
    return slice
  
  ## drawing functions ##
  def __prepare(self, node):
    box = node.border_box
    left, top, box_width, box_height = box
    right, bottom = left + box_width, top + box_height
    
    image = self.source
    repeat = expand_hv_value(self.repeat)
    width = self.__evaluate_image_width(node)
    slice = self.__evaluate_image_slice(node)
    
    fill = slice[0]
    iw, ih = image.width, image.height
    hrepeat, vrepeat = repeat
    wb, wr, wt, wl = width
    sb, sr, st, sl = map(float, slice[1:])
    
    # dimensions of the central part of an image
    scw = iw - sr - sl
    sch = ih - st - sb
    
    # sizes of large border parts (horiz. and vert. bars)
    h_bar_width  = box_width  - wl - wr
    v_bar_height = box_height - wt - wb
    
    # tile sizes
    if hrepeat == 'stretch':
      h_tile_top_width = h_tile_bottom_width = h_bar_width
    elif hrepeat == 'repeat':
      h_tile_top_width    = int(scw * (wt / st))
      h_tile_bottom_width = int(scw * (wb / sb))
    elif hrepeat == 'round':
      h_tile_width = lambda th: h_bar_width / round(h_bar_width / float(th))
      h_tile_top_width    = h_tile_width(wt)
      h_tile_bottom_width = h_tile_width(wb)
    else:
      raise ValueError(
        'Invalid value for background-image-repeat: %r' % hrepeat)
    
    if vrepeat == 'stretch':
      v_tile_left_height = v_tile_right_height = v_bar_height
    elif vrepeat == 'repeat':
      v_tile_left_height  = int(sch * (wl / sl))
      v_tile_right_height = int(sch * (wr / sr))
    elif vrepeat == 'round':
      v_tile_height = lambda tw: v_bar_height / round(v_bar_height / float(tw))
      v_tile_left_height  = v_tile_height(wl)
      v_tile_right_height = v_tile_height(wr)
    else:
      raise ValueError(
        'Invalid value for background-image-repeat: %r' % hrepeat)
    
    tiling_arguments = {
      'top-left': {
        'rect': (left, top, wl, wt),
        'tile_size': (wl, wt),
        'texcoords': rect_from_sides(
          left = 0., top = 1.,
          right = sl / iw, bottom = 1. - st / ih
        )
      },
      'top': {
        'rect': (left + wl, top, h_bar_width, wt),
        'tile_size': (h_tile_top_width, wt),
        'texcoords': rect_from_sides(
          left = sl / iw, top = 1.,
          right = 1. - sr / iw, bottom = 1 - st / ih
        )
      },
      'top-right': {
        'rect': (right - wr, top, wr, wt),
        'tile_size': (wr, wt),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = 1.,
          right = 1., bottom = 1. - st / ih
        )
      },
      'left': {
        'rect': (left, top + wt, wl, v_bar_height),
        'tile_size': (wl, v_tile_left_height),
        'texcoords': rect_from_sides(
          left = 0., top = 1. - st / ih,
          right = sl / iw, bottom = sb / ih
        )
      },
      'right': {
        'rect': (right - wr, top + wt, wr, v_bar_height),
        'tile_size': (wr, v_tile_right_height),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = 1. - st / ih,
          right = 1., bottom = sb / ih
        )
      },
      'bottom-left': {
        'rect': (left, bottom - wb, wl, wb),
        'tile_size': (wl, wb),
        'texcoords': rect_from_sides(
          left = 0., top = sb / ih,
          right = sl / iw, bottom = 0.
        )
      },
      'bottom': {
        'rect': (left + wl, bottom - wb, h_bar_width, wb),
        'tile_size': (h_tile_bottom_width, wb),
        'texcoords': rect_from_sides(
          left = sl / iw, top = sb/ ih,
          right = 1. - sr / iw, bottom = 0.
        )
      },
      'bottom-right': {
        'rect': (right - wr, bottom - wb, wr, wb),
        'tile_size': (wr, wb),
        'texcoords': rect_from_sides(
          left = 1. - sr / iw, top = sb / ih,
          right = 1., bottom = 0.
        )
      },
    }
    if fill:
      tiling_arguments['center'] = {
        'rect': (left + wl, top + wt, h_bar_width, v_bar_height),
         # size and height are resized like those of the
         # top and left image slices, respectively:
        'tile_size': (h_tile_top_width, v_tile_left_height),
        'texcoords': rect_from_sides(
          left = sl / iw, top = 1. - st / ih,
          right = 1. - sr / iw, bottom = sb / ih
        )
      }
    
    texture = image.get_texture()
    self.__vertices  = []
    self.__texcoords = []
    
    for kwargs in tiling_arguments.itervalues():
      v, tc = texturing.tile(texture, action='evaluate', **kwargs)
      self.__vertices.extend(v)
      self.__texcoords.extend(tc)
    
    # now optimization
    self.__vertices_count = len(self.__vertices)
    self.__vertices  = texturing.to_buffer(self.__vertices )
    self.__texcoords = texturing.to_buffer(self.__texcoords)
  
  def on_change(self):
    self.__vertices = self.__texcoords = None


from .border import Border
Border.subnames.append('image')
Border.defaults['image'] = BorderImage
_default_border = styles['*'].border
_default_border.set_by_subname('image', BorderImage({
  'source': 'none',
  'slice': 100., # TODO percent class?
  'width': 1, # NOT pixels => TODO separate pixel length class
  'outset': 0,
  'repeat': 'stretch',
}))
