import matplotlib.pyplot as plot
import numpy
import pyfits
from scipy.ndimage import zoom
from scipy import misc
from matplotlib.widgets import Slider, Button, RadioButtons





class ImageObject:
    def __init__(self, image, sampling):
        self.master_image = image
        self.current_image = image
        self.master_sampling = sampling
        self.current_sampling = sampling
        imsize = numpy.shape(image)
        self.xsize_arcsecs = imsize[1] * sampling
        self.ysize_arcsecs = imsize[2] * sampling 
        self.current_xsize_arcsecs = imsize[1] * sampling
        self.current_ysize_arcsecs = imsize[2] * sampling
    def update_sampling(self, new_sampling):
        zoom_factor = self.master_sampling / new_sampling
        self.current_sampling = new_sampling
        self.current_image = zoom(self.master_image, (zoom_factor, zoom_factor, 1.))
    def display_current(self):
        plot.imshow(self.current_image)
    def return_image(self):
        return self.current_image


def image_obj_test(sampling):
    wfc3_pixscale = .05
    im = misc.imread('hubble_galaxies/ngc6050.jpg')
    obj = ImageObject(im, wfc3_pixscale)
    obj.update_sampling(sampling)
    obj.display_current()


if __name__ == "__main__":
    #testing slider
    wfc3_pixscale = .05
    im = misc.imread('hubble_galaxies/ngc6050.jpg')
    obj = ImageObject(im, wfc3_pixscale)
    curr_im = obj.current_image
    fig, ax = plot.subplots()
    plot.subplots_adjust(left = .15, bottom = .25)
    l = plot.imshow(curr_im)
    samp_ax = plot.axes([.15, .1, .65, .03])
    samp_slider = Slider(samp_ax, 'Sampling', .05, 6., valinit = .05)
    def update(val):
        obj.update_sampling(samp_slider.val)
        l.set_data(obj.current_image)
        plot.draw()
    samp_slider.on_changed(update)
    plot.show()
