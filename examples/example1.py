import sys
sys.path.append('..')

import pyglet, cocos, cocosgui
from cocos.director import director

director.init(width=800, height=600, \
              caption='cocos2d-gui demo')
layer = cocos.layer.util_layers.ColorLayer(0, 66, 0, 255)
scene = cocos.scene.Scene(layer)

from cocosgui.layouts import VerticalLayout, HorizontalLayout
from cocosgui.buttons import Button
from cocosgui.editors import TextEdit
from cocosgui.windows import CenteredWindow
from cocosgui.static  import Image
window = CenteredWindow()
vlayout = VerticalLayout()
hlayout = HorizontalLayout()
# loading images
img1 = Image(pyglet.image.load('python-logo.png'))
img2 = Image(pyglet.image.load('cocos.png'))
img3 = pyglet.image.load('granite_frame.png')
# setting style for img1
img1.style['border'] = 5, 'solid', 'green'
img1.style['background-color'] = 'darkgreen'
img1.pseudostyle('focus')['border-right-color'] = 'cyan'
img1.pseudostyle('active')['border-left-color'] = 'magenta'
img1.pseudostyle('hover')['border-top-color'] = 'hsla(0, 100%, 50%, 0.5)'
img1.style['border-style'] = 'inset'
# setting style for img2
img2.style['border'] = 5, 'outset', 'blue'
img2.style['background-color'] = 'darkblue'
img2.pseudostyle('hover')['background-color'] = 'blue'
img2.pseudostyle('hover')['border'] = 5, 'inset', 'blue'
img2.pseudostyle('active')['background-color'] = '#003fff'
hlayout.add(img1)
hlayout.add(img2)
# setting style for vlayout (mainly, border-image)
vlayout.style['padding'] = 10
vlayout.style['border']  = 17, 'solid', '#000000'
vlayout.style['background'] = '#DDDDDD'
vlayout.style['border-image-source'] = img3
vlayout.style['border-image-slice'] = ('fill', 17)
vlayout.style['border-image-repeat'] = 'repeat'
btn = Button('I will be a button.')
btn.style['width' ] = 100
btn.style['height'] = 16
edt = TextEdit(text='Edit me! (Latin characters only...)')
edt.style['width'] = 150
edt.style['height'] = 16
vlayout.add(hlayout)
#vlayout.add(img2)
vlayout.add(btn)
vlayout.add(edt)
window.add(vlayout)
window.attach = (-20, -50.) # int = px, float = %
window.order()

layer.add(window)
director.run(scene)
