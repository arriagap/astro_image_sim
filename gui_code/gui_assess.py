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
        self.image_selection_menu.addItem('Galaxy Simulation 2')
        self.image_selection_menu.addItem('Galaxy Image 1')
        self.image_selection_menu.addItem('Galaxy Image 2')
        self.image_selection_menu.addItem('Jupiter Simulation')
        self.image_selection_menu.addItem('Jupiter Image 1')
        self.image_selection_menu.addItem('Jupiter Image 2')
        self.image_selection_menu.addItem('Star Formation Simulation 1')
        self.image_selection_menu.addItem('Star Formation Simulation 2')
        self.image_selection_menu.addItem('Star Formation Simulation 3')
        self.image_selection_menu.addItem('Star Formation Image 1')
        self.image_selection_menu.addItem('Star Formation Image 2')
        self.image_selection_menu.addItem('Star Formation Image 3')
        self.image_selection_menu.addItem('Galaxy Cluster Image')
        self.image_selection_menu.addItem('Galaxy Cluster Simulation')


        self.image_selection_menu.activated[str].connect(self.image_selection)
        vbox.addWidget(self.image_selection_menu)


        label_objsize = QLabel('Object Size (degrees)')
        self.objsizebox = QLineEdit()
        objsize_layout = QHBoxLayout()
        objsize_layout.addWidget(label_objsize)
        objsize_layout.addWidget(self.objsizebox)
        vbox.addLayout(objsize_layout)
        
        label_imsize = QLabel('Image Size (meters)   ')
        self.imsizebox = QLineEdit()
        imsize_layout = QHBoxLayout()
        imsize_layout.addWidget(label_imsize)
        imsize_layout.addWidget(self.imsizebox)

        vbox.addLayout(imsize_layout)
        self.updatebutton = QPushButton('Calculate')
        vbox.addWidget(self.updatebutton)

        self.oversampled = False
        self.fov_too_large = False
        self.message = QLabel('Messages:')
        vbox.addWidget(self.message)


        def onClicked():
            imsize = self.imsizebox.text()
            objsize = self.objsizebox.text()
            try: 
                imsize = float(imsize)
                objsize = float(objsize)
                objsize *= 3600.
                scale = objsize / imsize # arseconds / mm
                pixscale = scale * 18.3e-6 # arcseconds / pixel. 18.3 micron pixel size of H2RG 
                fov = 2048. * pixscale
                if pixscale != self.obj.current_sampling:
                    if pixscale > self.obj.master_sampling:
                        self.obj.update_sampling(pixscale)
                        self.imshow.set_data(self.obj.current_image)                
                        self.oversampled = False
                    else:
                        self.oversampled = True
                if fov < self.obj.xsize_arcsecs:
                    self.update_fov_square_size(fov)
                    self.current_fov = fov
                    self.fov_too_large = False
                else:
                    self.fov_too_large = True
                self.canvas.draw()
            except:
                QMessageBox.about(self, 'Error','Image size and object size must be numbers')
            self.refresh_message()
        self.updatebutton.clicked.connect(onClicked)


        
        # Initialize GUI
        self.main_frame.setLayout(vbox)
        self.setCentralWidget(self.main_frame)
    def refresh_message(self):
        if self.fov_too_large == False and self.oversampled == False:
            self.message.setText('Message: All OK')
        elif self.fov_too_large == False and self.oversampled == True:
            self.message.setText('Message: Pixel scale is higher than displayed')
        elif self.fov_too_large == True and self.oversampled == True:
            self.message.setText('Message: Pixel scale is higher than displayed and field of view is larger than current image')
        elif self.fov_too_large == True and self.oversampled == False:
            self.message.setText('Message: Field of view is larger than current image')
        return
        
    def init_draw(self):
        '''
        Sets up all of the matplotlib widgets
        '''
        self.fig.clear()
        self.image_axes = self.fig.add_subplot(111)
        # Initial image 
        # FIXME add null image
        self.current_pixscale = .05
        self.current_image_name = 'Galaxy Image 1'
#        im = misc.imread('galaxy_simulations/im1.jpg')
        im = misc.imread('galaxy_images/im1.jpg')
        self.obj = ImageObject(im, self.current_pixscale)
        self.image_object = self.obj.current_image
        
        # Initialize slider bars
        self.imshow = self.image_axes.imshow(self.image_object, interpolation='nearest', 
                                             extent = [-self.obj.xsize_arcsecs / 2., self.obj.xsize_arcsecs / 2.,
                                                       -self.obj.ysize_arcsecs / 2., self.obj.ysize_arcsecs / 2.])
        self.image_axes.set_title(self.current_image_name)
        self.image_axes.set_xlabel('Arcsecs')
        self.image_axes.set_ylabel('Arcsecs')
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
        self.image_axes.set_title(image_name)

        if image_name == 'Galaxy Image 1':
            im = misc.imread('galaxy_images/im1.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Image 2':
            im = misc.imread('galaxy_images/im2.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Image 3':
            im = misc.imread('galaxy_images/im3.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Image 4':
            im = misc.imread('galaxy_images/im4.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Simulation 1':
            im = misc.imread('galaxy_simulations/im1.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Simulation 2':
            im = misc.imread('galaxy_simulations/im2.jpg')
            pixscale = .01
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Jupiter Simulation':
            im = misc.imread('jupiter_simulation/jupiter_zoomout.png')
            pixscale = .02
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Jupiter Image 1':
            im = misc.imread('jupiter_images/im1.jpg')
            pixscale = .02
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Jupiter Image 2':
            im = misc.imread('jupiter_images/im2.jpg')
            pixscale = .005
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Simulation 1':
            im = misc.imread('star_formation_simulation/im1.gif')
            pixscale = .004 
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Star Formation Simulation 2':
            im = misc.imread('star_formation_simulation/im2.gif')
            pixscale = .004
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Star Formation Simulation 3':
            im = misc.imread('star_formation_simulation/im3.gif')
            pixscale = .004
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Image 1':
            im = misc.imread('star_formation_images/im1.jpg')
            pixscale = .002
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Image 2':
            im = misc.imread('star_formation_images/im2.jpg')
            pixscale = .002
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Star Formation Image 3':
            im = misc.imread('star_formation_images/im3.jpg')
            pixscale = .002
            self.obj = ImageObject(im, pixscale)
            self.image_update()

        if image_name == 'Galaxy Cluster Image':
            im = misc.imread('cosmology_images/im1.jpg')
            pixscale = .005
            self.obj = ImageObject(im, pixscale)
            self.image_update()
        if image_name == 'Galaxy Cluster Simulation':
            im = misc.imread('cosmology_simulation/actual_im1.jpg')
            pixscale = .005
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
            def update(val):
                self.imshow.set_data(self.obj.current_image)
                self.canvas.draw()
        else:
            pass
            #self.sample_slider.reset()


def main():
    app = QApplication(sys.argv)
    form = AppForm()
    form.show()
    app.exec_()

if __name__ == "__main__":
    main()
