from __future__ import print_function

import sys

from matplotlib.figure import Figure
from matplotlib.backend_bases import key_press_handler
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends import qt4_compat
from matplotlib import animation
import matplotlib.patches as patches
use_pyside = qt4_compat.QT_API == qt4_compat.QT_API_PYSIDE
import numpy
from scipy import misc
from resample import ImageObject
from matplotlib.widgets import Slider, Button, RadioButtons
from matplotlib import gridspec

if use_pyside:
    from PySide.QtCore import *
    from PySide.QtGui import *
else:
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *


class AppForm(QMainWindow):
    '''
    Master GUI. To initialize:
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()
    '''
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)
        # Creates GUI framework
        self.create_main_frame()
        # Plots initial image
        self.init_draw()
    def create_main_frame(self):
        self.main_frame = QWidget()

        # Figure parameters. 
        # FIXME Probably change figure parameters given computer resolution
        self.fig = Figure((10.0, 10.0), dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setParent(self.main_frame)
        self.canvas.setFocusPolicy(Qt.StrongFocus)
        self.canvas.setFocus()

        # Matplotlib move around 
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.main_frame)

        # Add figures to GUI
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)  # the matplotlib canvas
        vbox.addWidget(self.mpl_toolbar)

        # Image selection dropdown box
        self.image_selection_menu = QComboBox()
        self.image_selection_menu.addItem('Galaxy Simulation 1')
#        self.image_selection_menu.addItem('Galaxy Image 1')
#        self.image_selection_menu.addItem('Galaxy Image 2')
        self.image_selection_menu.addItem('Jupiter Narrow Field Simulation')
        self.image_selection_menu.addItem('Jupiter Wide Field Simulation')
        self.image_selection_menu.addItem('Star Formation Simulation 1')
        self.image_selection_menu.addItem('Star Formation Simulation 2')
        self.image_selection_menu.addItem('Star Formation Simulation 3')
#        self.image_selection_menu.addItem('Star Formation Image 1')
#        self.image_selection_menu.addItem('Star Formation Image 2')
        self.image_selection_menu.activated[str].connect(self.image_selection)
        vbox.addWidget(self.image_selection_menu)

        self.objsizebox = QLineEdit()
        vbox.addWidget(self.objsizebox)
        self.imsizebox = QLineEdit()
        vbox.addWidget(self.imsizebox)
        self.updatebutton = QPushButton('Derp')
        vbox.addWidget(self.updatebutton)

##########################

        def onClicked():
            imsize = self.imsizebox.text()
            objsize = self.objsizebox.text()
            print('fuck')
            try: 
                imsize = float(imsize)
                print(imsize)
                objsize = float(objsize)
                print(objsize)
                scale = objsize / imsize # arseconds / mm
                pixscale = scale * 18.3e-3 # arcseconds / pixel. 18.3 micron pixel size of H2RG 
                print(pixscale)
                fov = 2048. * pixscale
                print(fov)
                if pixscale != self.obj.current_sampling:
                    print('fucker')
                    if pixscale > self.obj.master_sampling:
                        self.obj.update_sampling(pixscale)
                        self.imshow.set_data(self.obj.current_image)
                
                if fov < self.obj.xsize_arcsecs:
                    self.update_fov_square_size(fov)
                    self.current_fov = fov
                    print('fuckerfucker')
                self.canvas.draw()
            except:
                QMessageBox.about(self, 'Error','Image size and object size must be numbers')
                
########################
        self.updatebutton.clicked.connect(onClicked)


        
        # Initialize GUI
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    def init_draw(self):
        '''
        Sets up all of the matplotlib widgets
        '''
        self.fig.clear()
        self.image_axes = self.fig.add_subplot(111)
        # Initial image 
        # FIXME add null image
        self.current_pixscale = .05
        im = misc.imread('galaxy_images/im1.jpg')
        self.obj = ImageObject(im, self.current_pixscale)
        self.image_object = self.obj.current_image
        
        # Initialize slider bars
        self.imshow = self.image_axes.imshow(self.image_object, interpolation='nearest', 
                                             extent = [-self.obj.xsize_arcsecs / 2., self.obj.xsize_arcsecs / 2.,
                                                       -self.obj.ysize_arcsecs / 2., self.obj.ysize_arcsecs / 2.])


        self.current_fov = 10.
        self.current_xloc = -self.current_fov / 2. 
        self.current_yloc = -self.current_fov / 2. 
        rectsize = 10.
        self.fov_square = patches.Rectangle((-self.current_fov / 2., - self.current_fov / 2.), rectsize, rectsize, fill = False, linewidth = 4.0, edgecolor = 'red')




        self.image_axes.add_artist(self.fov_square)
        def update(val):
            if self.sample_slider.val != self.obj.current_sampling:
                self.obj.update_sampling(self.sample_slider.val)
                self.imshow.set_data(self.obj.current_image)
            fov = self.fov_slider.val 
            self.update_fov_square_size(fov)
            self.current_fov = fov
            self.canvas.draw()

        def onclick(event):
            if event.xdata is not None and event.ydata is not None:
                loc = (event.xdata - self.current_fov / 2., event.ydata - self.current_fov / 2.)
                if event.inaxes == self.image_axes:
                    self.update_fov_square_loc(loc)
                    self.current_xloc = loc[0]
                    self.current_yloc = loc[1]
                    self.canvas.draw()
        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)
        self.canvas.draw()

    def update_fov_square_loc(self, newloc):
        self.fov_square.set_xy(newloc)
        

    def update_fov_square_size(self, rectsize): #add location later
        '''
        Adds a square centered around location
        '''
        center_xloc = self.current_xloc + self.current_fov / 2.
        center_yloc = self.current_yloc + self.current_fov / 2.
        new_xloc = center_xloc - rectsize / 2.
        new_yloc = center_yloc - rectsize / 2.
        self.fov_square.set_height(rectsize)
        self.fov_square.set_width(rectsize)
        self.current_xloc = new_xloc
        self.current_yloc = new_yloc
        self.fov_square.set_xy((new_xloc, new_yloc))

    def image_selection(self, image_name):
        ''' 
        Hacked together image selection. 
        Takes selection from the image_selection_menu widget 
        '''
        if image_name == 'Galaxy Image 1':
            im = misc.imread('galaxy_images/im1.jpg')
            pixscale = .05
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Image 2':
            im = misc.imread('galaxy_images/im2.jpg')
            pixscale = .05
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Simulation 1':
            im = misc.imread('galaxy_simulations/im1.jpg')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Jupiter Narrow Field Simulation':
            im = misc.imread('jupiter_simulation/jupiter_zoomin.png')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Jupiter Wide Field Simulation':
            im = misc.imread('jupiter_simulation/jupiter_zoomout.png')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Star Formation Simulation 1':
            im = misc.imread('star_formation_simulation/im1.gif')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Star Formation Simulation 2':
            im = misc.imread('star_formation_simulation/im2.gif')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Star Formation Simulation 3':
            im = misc.imread('star_formation_simulation/im3.gif')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Image 1':
            im = misc.imread('star_formation_images/im1.jpg')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Image 2':
            im = misc.imread('star_formation_images/im2.gif')
            pixscale = .1
            self.obj = ImageObject(im, pixscale)
            self.image_update()



    def image_update(self):
        '''
        Helper function to image selection, resets image and sliders
        '''

        self.imshow.set_data(self.obj.current_image)
        self.imshow.set_extent([-self.obj.xsize_arcsecs / 2., self.obj.xsize_arcsecs / 2., 
                                -self.obj.ysize_arcsecs / 2., self.obj.ysize_arcsecs / 2.])
        self.canvas.draw()
        if self.obj.master_sampling != self.current_pixscale:
            self.current_pixscale = self.obj.master_sampling
            self.sample_axis.cla()
            self.sample_slider = Slider(self.sample_axis, 'Sampling (arcsecs/pix)', self.current_pixscale, self.current_pixscale * 20., valinit = self.current_pixscale)
            def update(val):
                self.obj.update_sampling(self.sample_slider.val)
                self.imshow.set_data(self.obj.current_image)
                self.canvas.draw()
            self.sample_slider.on_changed(update)
        else:
            self.sample_slider.reset()


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
