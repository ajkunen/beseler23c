#!/usr/bin/env python3
# BSD 3-Clause License
#
# Copyright (c) 2020, Adam Kunen
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# Generates laser cutter SVG files to create negative carriers for the 
# Beseler 23C enlarger
# 
# See README
#

import math

#
# Define parameters of the overall paddle geometery
# regardless of film size
#

# bounding box on entire design
img_width  = 8.6
img_height = 6.5

# Major diameter of paddle
large_diam = 6.375
large_rad = large_diam/2.0

# Handle parameters
handle_width = 1.135
handle_length = 8.450 - large_diam
aligner_gap = 0.005

# Side of bottom ring
ring_diam = 4.725

# Large diam to handle fillet raidus
handle_fillet = 0.750

# handle end radius
handle_rad = 0.150


# create centerpoint for carrier
# this is the center of the large diameter, and the center of the image cutout
x_center = img_height/2.0
y_center = x_center

#
# Output opening tags
#
def makeHeader():
  s =  "<!DOCTYPE svg PUBLIC \"-//W3C//DTD SVG 1.1//EN\" \"http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd\">"
  s += "<svg version=\"1.1\" xmlns=\"http://www.w3.org/2000/svg\" xmlns:xlink=\"http://www.w3.org/1999/xlink\" xml:space=\"preserve\" width=\"%fin\" height=\"%fin\" viewBox=\"%f %f %f %f\">" % (img_width, img_height, 0.0, 0.0, img_width, img_height)
  return s

#
# Close out svg file
#
def makeFooter():
  return "</svg>\n"

#
# Draw outline of partial arc given center, radius starting and ending angle (radians)
# if moveTo is True, it lift's the pen, otherwise it just continues path
#
def drawArc(center, rad, theta0, theta1, moveTo):
    one_degree = (2.0*math.pi)/360.0

    dtheta = one_degree*0.5
    num_segments = 1+int(abs(theta1-theta0)/dtheta)
    dtheta = (theta1-theta0)/num_segments

    path = ""

    for i in range(0, num_segments):
        theta_i = theta0 + i*dtheta
        theta_i1 = theta_i + dtheta

        if i == 0 and moveTo:
            point0 = [center[0]+math.cos(theta_i)*rad, 
                      center[1]+math.sin(theta_i)*rad]
            path += " M%f,%f" % (point0[0], point0[1])
        
        point1 = [center[0]+math.cos(theta_i1)*rad, 
                  center[1]+math.sin(theta_i1)*rad]

        path += " L%f,%f" % (point1[0], point1[1])
    
    return path

#
# Draws a rectangle, lifting pen to start
#
# p is the location of upper-left corner
#
def drawRect(p, width, height):
    path = "M%f,%f L%f,%f L%f,%f L%f,%f L%f,%f" %  (
             p[0], p[1],
             p[0]+width, p[1],
             p[0]+width, p[1]+height,
             p[0], p[1]+height,
             p[0], p[1])

    return path


#
# Creates outline of paddle
#
def makePaddleOutline():
  
  s = "<!-- Paddle outline -->\n"

  #compute angle which handle intersects large diameter 
  handle_angle = math.tan(handle_width/large_diam)


  # draw handle fillet
  handle_theta0 = math.asin( (handle_width/2+handle_fillet) / (large_rad+handle_fillet) )
  handle_theta1 = math.pi/2 - handle_theta0
  
  fillet_dist = handle_fillet + large_rad
  fillet_centerA = [fillet_dist*math.cos(handle_theta0) + x_center,
                   y_center - fillet_dist*math.sin(handle_theta0)]
  fillet_centerB = [fillet_dist*math.cos(handle_theta0) + x_center,
                   fillet_dist*math.sin(handle_theta0) + y_center]

  handle_angle = handle_theta0
  outline = drawArc([x_center, y_center], large_diam/2.0, handle_angle, 2.0*math.pi-handle_angle, True)

  # draw handle fillet
  outline += drawArc(fillet_centerA, handle_fillet, 1.5+handle_theta1, 0.5*math.pi, False)

  # draw handle corner rounds
  handle_end = handle_length+x_center+large_diam/2.0
  outline += drawArc([handle_end-handle_rad, y_center-0.5*handle_width+handle_rad], handle_rad, -0.5*math.pi, 0.0, False)
  outline += drawArc([handle_end-handle_rad, y_center+0.5*handle_width-handle_rad], handle_rad, 0.0, 0.5*math.pi, False)

  # draw handle fillet
  outline += drawArc(fillet_centerB, handle_fillet, 1.5*math.pi, 1.5*math.pi-handle_theta1, False)

  # draw entire outline
  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s z\" />\n\n" % (outline)
  return s


#
# Draw hole to make it easier to separate top from bottom 
#
def makePaddleSeparatorHoles():

  s = "<!-- Paddle separator holes -->\n"
  
  R = handle_width/2 * 0.6
  holes  = drawArc([x_center+large_rad+handle_length-handle_width/2, y_center], R, 0, 2*math.pi, True)
  holes += drawArc([x_center-large_rad+R*1.2, y_center], R*0.8, 0, 2*math.pi, True)
  
  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s z\" />\n\n" % (holes)

  return s


#
# Draw film cutout
#
def makeFilmCutout(cut_width, cut_height, film_width, aligner_diam):

  s = "<!-- Film cutout %.4fx%.4f\" -->\n" % (cut_width, cut_height)
  
  # draw cutout
  cut_x = x_center - cut_height/2
  cut_y = y_center - cut_width/2

  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"M%f,%f l%f,0 l0,%f l%f,0 z\" />\n\n" % (
       cut_x, cut_y,
       cut_height,
       cut_width,
       -cut_height) 

  return s


#
# Draw aligners
#
def makeAligners(cut_width, cut_height, film_width, aligner_diam, scale):

  s = "<!-- Aligner pins %.4f\" diam -->\n" % (aligner_diam*scale)
  
  cut_x = x_center - cut_height/2
  cut_y = y_center - cut_width/2
  
  aligners = ""

  aligner_rad = aligner_diam/2

  # aligner 0
  p = [x_center-film_width/2-aligner_rad, y_center-cut_width/2+aligner_rad]
  aligners += drawArc(p, aligner_rad*scale, 0, 2*math.pi, True)

  # aligner 1
  p = [x_center+film_width/2+aligner_rad, y_center-cut_width/2+aligner_rad]
  aligners += drawArc(p, aligner_rad*scale, 0, 2*math.pi, True)

  # aligner 2
  p = [x_center-film_width/2-aligner_rad, y_center+cut_width/2-aligner_rad]
  aligners += drawArc(p, aligner_rad*scale, 0, 2*math.pi, True)

  # aligner 3
  p = [x_center+film_width/2+aligner_rad, y_center+cut_width/2-aligner_rad]
  aligners += drawArc(p, aligner_rad*scale, 0, 2*math.pi, True)

  # draw aligners
  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s\" />\n\n" % aligners 

  return s





#
# Draw ring
#
def makeRing():
  
  s = "<!-- Ring  OD=%.4f\", ID=%.4f\" -->\n" % (ring_diam, ring_diam-1.0)

  ring  = drawArc([x_center, y_center], ring_diam/2, 0.0, 2*math.pi, True)
  ring += drawArc([x_center, y_center], ring_diam/2-0.5, 0.0, 2*math.pi, True)
  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s\" />\n\n" % ring

  return s

#
# Draw ring alignment holes
#
def makeRingAligners():
  
  s = "<!-- Ring alignment holes  -->\n"
  
  off = ring_diam/2 - 0.25
  holes  = drawArc([x_center, y_center-off], 0.125, 0.0, 2*math.pi, True)
  holes += drawArc([x_center, y_center+off], 0.125, 0.0, 2*math.pi, True)
  holes += drawArc([x_center-off, y_center], 0.125, 0.0, 2*math.pi, True)
  holes += drawArc([x_center+off, y_center], 0.125, 0.0, 2*math.pi, True)

  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s\" />" % holes

  return s


#
# Draw extra alignment pins
#
def makeExtraPins(pin_diam):
  
  s = "<!-- Extra alignment pins  -->\n"
  
  off = (large_rad-0.625)/math.sqrt(2.0)
  
  holes  = drawArc([x_center-off, y_center-off], pin_diam/2, 0.0, 2*math.pi, True)
  holes += drawArc([x_center-off, y_center+off], pin_diam/2, 0.0, 2*math.pi, True)
  holes += drawArc([x_center+off, y_center-off], pin_diam/2, 0.0, 2*math.pi, True)
  holes += drawArc([x_center+off, y_center+off], pin_diam/2, 0.0, 2*math.pi, True)

  s += "  <path stroke=\"black\" fill=\"none\" stroke-width=\".01\" d=\"%s\" />" % holes

  return s




#
# Create top layer
#
def genTop(name, cut_width, cut_height, film_width, aligner_diam, extra_pins):
  
  s =  makeHeader()

  s += makePaddleOutline()
  s += makeFilmCutout(cut_width, cut_height, film_width, aligner_diam)
  s += makeAligners(cut_width, cut_height, film_width, aligner_diam, 1.0)
  if extra_pins:
    s += makeExtraPins(0.750)


  s += makeFooter()

  # write to file
  fh = open(name, "w")
  fh.write(s)


#
# Create bottom layer
#
def genBottom(name, cut_width, cut_height, film_width, aligner_diam, extra_pins):
  
  s =  makeHeader()

  s += makePaddleOutline()
  s += makePaddleSeparatorHoles()
  s += makeFilmCutout(cut_width, cut_height, film_width, aligner_diam)
  s += makeAligners(cut_width, cut_height, film_width, aligner_diam, 0.5)
  if extra_pins:
    s += makeExtraPins(0.375)
  s += makeRingAligners()

  s += makeFooter()

  # write to file
  print("    - writing %s" % name)
  fh = open(name, "w")
  fh.write(s)

#
# Create ring layer
#
def genRing(name, cut_width, cut_height, film_width, aligner_diam, extra_pins):
  
  s =  makeHeader()

  s += makeRing()
  s += makeRingAligners()

  s += makeFooter()

  # write to file
  print("    - writing %s" % name)
  fh = open(name, "w")
  fh.write(s)

#
# Create all debugging layer
#
def genAll(name, cut_width, cut_height, film_width, aligner_diam, extra_pins):
  
  s =  makeHeader()

  s += makePaddleOutline()
  s += makePaddleSeparatorHoles()
  s += makeFilmCutout(cut_width, cut_height, film_width, aligner_diam)
  s += makeAligners(cut_width, cut_height, film_width, aligner_diam, 1.0)
  s += makeAligners(cut_width, cut_height, film_width, aligner_diam, 0.5)
  if extra_pins:
    s += makeExtraPins(0.750)
    s += makeExtraPins(0.375)
  s += makeRing()
  s += makeRingAligners()

  s += makeFooter()

  # write to file
  print("    - writing %s" % name)
  fh = open(name, "w")
  fh.write(s)



#
# Create all 3 layers for carrier
#
def genCarrier(name, cut_width, cut_height, film_width, aligner_diam, extra_pins):
  
  # Create Top
  genTop("%s_top.svg"%name, cut_width, cut_height, film_width, aligner_diam, extra_pins)

  # Create Bottom
  genBottom("%s_bottom.svg"%name, cut_width, cut_height, film_width, aligner_diam, extra_pins)

  # Create Ring
  genRing("%s_ring.svg"%name, cut_width, cut_height, film_width, aligner_diam, extra_pins)

  # Create single drawing with all 3 layers for debugging
  genAll("%s_all.svg"%name, cut_width, cut_height, film_width, aligner_diam, extra_pins)


# 
# Main: Draw all designs
#

if __name__ == "__main__":
  print("Besseler 23C Film Carrier Generator")

  print("  - Creating 35mm standard carrier")
  genCarrier(name="23C_35mm", cut_width=1.425, cut_height=0.945, film_width=1.378+0.010, aligner_diam=0.500, extra_pins=True)

  print("  - Creating 120 film 6x7cm carrier")
  genCarrier(name="23C_120_6x7cm", cut_width=2.675, cut_height=2.200, film_width=2.425+0.010, aligner_diam=0.750, extra_pins=False)

  print("  - Creating 120 film 6x6cm carrier")
  genCarrier(name="23C_120_6x6cm", cut_width=2.200, cut_height=2.200, film_width=2.425+0.010, aligner_diam=0.750, extra_pins=False)
  
  print("done")


