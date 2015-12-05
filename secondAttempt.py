#!/usr/bin/python

import Image
from math import *
 
img = Image.new( 'RGB', (255,255), "grey") # create a new grey image
pixels = img.load() # create the pixel map

width, height = img.size

for i in range(width):    # for every pixel:
    for j in range(height):
        pixel_value=int(floor(128+128*sin(i*2*pi/width)*cos(j*6*pi/height)))
        #        if (i%8==0 and j%8==0):
        pixels[i,j]=(pixel_value,0,0)
            

# for i in range(width):    # for every pixel:
#     for j in range(height):
#         if (i < width/2):
#             if (j < height/2):
#                 pixels[i,j] = (255, 0, 0)
#             else:
#                 pixels[i,j] = (0, 255, 0)
#         else:
#             if (j < height/2):
#                 pixels[i,j] = (0, 0, 255)
#             else:
#                 pixels[i,j] = (255, 255, 255)
 
img.save("newfile.png")

quit()
