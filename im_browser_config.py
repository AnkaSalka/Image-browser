"""
    Image browser.
To run this program you have to install:
    Tkinter
    PIL and ImageTk (it is available here http://pythonware.com/products/pil/).
    swampy (it is available here thinkpython.com/swampy).
 """

from swampy.Gui import *
from Tkinter import PhotoImage
from PIL import Image 
from PIL import ImageTk
from os import listdir
from os.path import isfile, join
from copy import copy
import tkMessageBox


class Draggable(Item):
    """A Canvas Item with bindings for dragging and dropping.

    Given an item, Draggable(item) creates bindings and returns
    a Draggable object with the same canvas and tag as the original.
    """
    def __init__(self, item):
        self.canvas = item.canvas
        self.tag = item.tag
        # size of the resized window (canvas remains unchangable)
        self.w = item.w
        self.h = item.h
        bounds = self.bbox()
        # difference between photo size and canvas size
        self.dw = bounds[1][0] - bounds[0][0] - self.w 
        self.dh = bounds[0][1] - bounds[1][1] - self.h
        self.bind('<ButtonPress-3>', self.select)
        self.bind('<B3-Motion>', self.drag)
        

    # the following event handlers take an event object as a parameter
    def select(self, event):
        """Selects this item for dragging."""
        self.dragx = event.x
        self.dragy = event.y
        
    def drag(self, event):
        """Move this item using the pixel coordinates in the event object."""
        # see how far we have moved
        dx = event.x - self.dragx 
        dy = event.y - self.dragy
        self.dragx = event.x
        self.dragy = event.y
        bounds = self.bbox()
        # markers of movement
        a = 0
        b = 0
        # setting boundaries (photo cannot be moved to the outside of canvas)
        if self.w - self.canvas.width/2 <= bounds[1][0] + dx <= self.w - self.canvas.width/2 + self.dw:
            a = 1
        if self.canvas.height/2 <= bounds[0][1] - dy <=  self.canvas.height/2 + self.dh:
            b = 1
        self.move(a*dx,b*dy)


class Images(object):
    """ Objects that stores image and photo.
        attributes: image - object that can be resized, rotated
                    photo - object that is displayed at canvas"""
    def __init__(self,im_path):
        self.image = Image.open(im_path)
        self.photo = ImageTk.PhotoImage(self.image)
        
    def resize(self,other,height=35):
        """ Proportionally resizes image to the given height;
            saves changes in object: other
            input object self remains unchangable"""
        r = (self.image.size[0])/float(self.image.size[1])
        other.image = self.image.resize((int(r*height),height))
        other.photo = ImageTk.PhotoImage(other.image)
            
    def reshowOnCa(self,other,cs,height,width,x=0,y=0):
        """ Resizes image (if needed - if size exceeds size of canvas/window) and displays it on canvas
        self: object which image is used
        other: object that stores changes
        cs: canvas
        x,y: coordinates of displaying photo"""
        if self.image.size[1] > height or self.image.size[0] > width:
            self.resize(other,height)
            cs.image([x,y], image=other.photo)
        else:
            other.photo = ImageTk.PhotoImage(self.image)
            cs.image([x,y], image=other.photo)
        

class Im_br(Gui):
    """ Creates Image browser """
    def __init__(self,width=800,height=420):
        Gui.__init__(self)

        # creating window
        self.col([0,1,0,0])
        
        self.row()
        # creating row of icons - rotate, maximise, minimise
        self.rt = self.make_icon('rotate_right.png')
        self.lt = self.make_icon('rotate_left.png')
        self.b_rt = self.bu(image=self.lt,command=self.rot_im_left,height = 35)
        self.b_lt = self.bu(image=self.rt,command=self.rot_im_right,height = 35)
        self.Max = self.make_icon('max.png')
        self.Min = self.make_icon('min.png')
        self.b_max = self.bu(image=self.Max,command=self.max_show,height = 35)
        self.b_min = self.bu(image=self.Min,command=self.min_show,height = 35)
        self.endrow()
        
        # creating canvas and welcome-photo
        self.cs = self.ca(width,height)
        self.cs.bind('<Configure>',self.configure)
        Im_br.obj = Images('press_to_cont.jpg')
        
        # widget for choosing directory
        self.en = self.en(text=' Set a directory ... ')
        self.en.bind('<Return>',self.open_dir)
        self.b = self.bu(text='OK',command=self.open_dir)

        

    # class attribute
    np = 0 # counter for files that cannot be read

    def configure(self,ev):
        """ When window configures displays existing photo on canvas with corresponding coordinates. """
        # Note: size of the canvas remains unchangable
        self.cs.delete('all')
        Im_br.e = ev
        Im_br.x = ev.width/2 - self.cs.width/2
        Im_br.y = self.cs.height/2 - ev.height/2
        Im_br.backup = copy(Im_br.obj)
        Im_br.obj.reshowOnCa(Im_br.backup,self.cs,ev.height,ev.width,Im_br.x,Im_br.y)
        
    def open_dir(self,event=None):
        """ Opens directory and displays images """
        try:
            directory = self.en.get()
            Im_br.files = [] # list of files in the directory
            Im_br.count = 0 # counter for files in the directory
            Im_br.files = [join(directory, f) for f in listdir(directory)
                     if isfile(join(directory, f))]
            # catching directory without files
            if Im_br.files == []:
                tkMessageBox.showinfo('Error',message="There is no files in this directory.\nPlease, choose another one.")
                return
            self.cs.delete('all')
            self.another_photo()
            self.cs.bind('<ButtonPress-1>',self.another_photo)
        except WindowsError:
            # catching unexisting directory
            tkMessageBox.showinfo('Error',message="Directory cannot be found.\nPlease, choose another one.")
            return

    def another_photo(self,event=None):
        """ Displays image with path files[count] on canvas """
        # looping review of photos
        if Im_br.count == (len(Im_br.files) - 1): Im_br.count = -1
        if Im_br.count == - len(Im_br.files): Im_br.count = 0
        
        # next or previous photo
        if len(Im_br.files) <> 1:
            self.next_prev(event)
        
        # printing photo on canvas
        try:
            Im_br.obj = Images(Im_br.files[Im_br.count]) # stores real size of image
            Im_br.backup = copy(Im_br.obj) # is displayed on the canvas
            Im_br.obj.reshowOnCa(Im_br.backup,self.cs,Im_br.e.height,Im_br.e.width,Im_br.x,Im_br.y)
        except IOError:
            # counter for catching an unappropriate directory
            Im_br.np += 1
            # catching directory without images to read
            if Im_br.np >= len(Im_br.files) - 1 and event == None:
                tkMessageBox.showinfo('Error',message="This directory cannot be read.\nPlease, choose another one.")
                return
            # skipping to another file
            else: self.another_photo(event=event)
                                      
          
    def next_prev(self,event):
        """ Depending on event coordinate x, next or previous image will be shown """
        if event <> None:
            if event.x >= Im_br.x + self.cs.width/2:
                Im_br.count += 1
            elif event.x < Im_br.x + self.cs.width/2:
                Im_br.count += -1
        else:
            Im_br.count += 1
            

    def rot_im_right(self):
        """ Rotates image clockwise """
        try:
            Im_br.obj.image = Im_br.obj.image.rotate(360-90)
            Im_br.obj.reshowOnCa(Im_br.backup,self.cs,Im_br.e.height,Im_br.e.width,Im_br.x,Im_br.y)
        except AttributeError: return
        

    def rot_im_left(self,event=None):
        """ Rotates image counterclockwise """
        try:
            Im_br.obj.image = Im_br.obj.image.rotate(90)
            Im_br.obj.reshowOnCa(Im_br.backup,self.cs,Im_br.e.height,Im_br.e.width,Im_br.x,Im_br.y)
        except AttributeError: return

    def max_min_show(self,sign = 1,event = None):
        """ Maximise or minimise an image with step 50 pixels
            sign: detemines max (=1) or min(=-1) the image;
            creates canvas item that can be draggable """
        (xx,yy) = Im_br.backup.image.size
        Im_br.obj.resize(Im_br.backup,height=yy+sign*50)
        Im_br.item = self.cs.image([Im_br.x,Im_br.y], image=Im_br.backup.photo) # is used for moving image
        Im_br.item.w = Im_br.e.width
        Im_br.item.h = Im_br.e.height
        Im_br.item = Draggable(Im_br.item)
         
              

    def max_show(self,event=None):
        """ Maximise an image with step 50 pixels """
        try:
            (xx,yy) = Im_br.backup.image.size
            if xx < 2000 and yy < 2000:
                self.max_min_show(sign = 1,event = event)
            else: return
        except AttributeError: return
        
    def min_show(self,event=None):
        """ Minimise an image with step 50 pixels """
        try:
            (xx,yy) = Im_br.backup.image.size
            if xx > 50 and yy > 50:
                self.max_min_show(sign = -1,event = event)
            else: return
        except AttributeError: return

    def make_icon(self,name):
        """ Creates photo, that will be used for making an icon.
            name : path to the image """
        icon = Images(name)
        icon.resize(icon)
        return icon.photo    

if __name__ == '__main__':
    
    g = Im_br(width=800,height=420)
    g.mainloop()

