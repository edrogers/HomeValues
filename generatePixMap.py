#!/usr/bin/python

from PythonMagick import *
# import PythonMagick
from PIL import Image
import ImageDraw

#Create a 5-d array to describe the RGB values for every x-y
xMax=2
yMax=3
R,G,B = 0,1,2
pixArray=[[[y+yMax*x+1 for color in range(3)] for y in range(yMax)] for x in range(xMax)]
for x in pixArray:
    for y in x:
        print(pixArray.index(x),x.index(y))

        


img=Image.new('RGB',(30, 30),'red')
img.save("outfile.png")
#draw=ImageDraw.Draw(img)
#img_pm=PythonMagick.Image()
#img.display()
# pixels=img.getdata()
# img.write('test1.png')
# data=file('test1.png','rb').read()
# img=PythonMagick.Image(PythonMagick.Blob(data))
# img.write('test2.png')
# print "now you should have two png files"
# img.show()
# im = Image.open("output.png")

# print im.format, im.size, im.mode

quit()
