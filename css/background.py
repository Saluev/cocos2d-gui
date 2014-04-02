from . import to_words, from_words, StylesContainer


class Background(StylesContainer):
  prefix = 'background'
  defaults = {
    'color': 'transparent',
    'position': (0, 0), # TODO 0%, 0%
    'size': 'auto',
    'repeat': 'repeat',
    'origin': 'padding-box',
    'clip': 'border-box',
   #'attachment': 'scroll',
    'image': None,
  }
  subnames = defaults.keys()
  
  def get_as_value(self):
    return self