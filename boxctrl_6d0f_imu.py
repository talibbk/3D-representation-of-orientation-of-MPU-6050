#!/usr/bin/env python

from OpenGL.GL import *
from OpenGL.GLU import *
import pygame
from pygame.locals import *
import serial
import time
import csv

#ser = serial.Serial('/dev/tty.usbserial', 38400, timeout=1)
ser = serial.Serial('/dev/cu.usbmodem14101', 38400, timeout=1)

ax = ay = az = 0.0
yaw_mode = False
record_mode = False
axis_mode = False

def resize(width, height):
    if height==0:
        height=1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)     #(field of view, aspect ratio, zNear, ZFar)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def drawText(position, textString):     
    font = pygame.font.SysFont ("Courier", 18, True)
    textSurface = font.render(textString, True, (255,255,255,255), (0,0,0,255))     
    textData = pygame.image.tostring(textSurface, "RGBA", True)     
    glRasterPos3d(*position)     
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def storeCsv(ay,ax,az):
        #Header for CSV
    with open('test1.csv', 'a') as logfile:
        fieldnames = ['Pitch','Roll','Yaw']
        writer = csv.DictWriter(logfile, fieldnames = fieldnames)

    #Write header only if its not present  
        if logfile.tell() == 0:
            writer.writeheader()

    #Write data to CSV
        writer.writerow({'Pitch':ay, 'Roll':ax, 'Yaw':az})
    
def draw():
    global rquad
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);	
    
    glLoadIdentity()
    glTranslatef(0,0.0,-7.0)

    osd_text = "pitch: " + str("{0:.2f}".format(ay)) + ", roll: " + str("{0:.2f}".format(ax)) #displaying upto 2 decimal place

    if yaw_mode:
        osd_line = osd_text + ", yaw: " + str("{0:.2f}".format(az))
    else:
        osd_line = osd_text

    drawText((-2,-2, 2), osd_line) #position of text

    # the way I'm holding the IMU board, X and Y axis are switched 
    # with respect to the OpenGL coordinate system
    if yaw_mode:                             # experimental
        glRotatef(az, 0.0, 1.0, 0.0)  # Yaw,   rotate around y-axis
    else:
        glRotatef(0.0, 0.0, 1.0, 0.0)
    glRotatef(ay ,1.0,0.0,0.0)        # Pitch, rotate around x-axis
    glRotatef(-1*ax ,0.0,0.0,1.0)     # Roll,  rotate around z-axis
    
    print(osd_line)

    glBegin(GL_QUADS)	
    #defining  faces of rectangle
    glColor3f(0.0,1.0,0.0)
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f( 1.0, 0.2, 1.0)		

    glColor3f(1.0,0.5,0.0)	
    glVertex3f( 1.0,-0.2, 1.0)
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		

    glColor3f(1.0,0.0,0.0)		
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2, 1.0)		

    glColor3f(1.0,1.0,0.0)	
    glVertex3f( 1.0,-0.2,-1.0)
    glVertex3f(-1.0,-0.2,-1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f( 1.0, 0.2,-1.0)		

    glColor3f(0.0,0.0,1.0)	
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2,-1.0)		
    glVertex3f(-1.0,-0.2,-1.0)		
    glVertex3f(-1.0,-0.2, 1.0)		

    glColor3f(1.0,0.0,1.0)	
    glVertex3f( 1.0, 0.2,-1.0)
    glVertex3f( 1.0, 0.2, 1.0)
    glVertex3f( 1.0,-0.2, 1.0)		
    glVertex3f( 1.0,-0.2,-1.0)		
    glEnd()	

def axes():
    #Draw coordinate axes.
    #Red = Positive X direction - Roll
    #White = Positive Z direction - Yaw
    #Blue = Positive Y direction - Pitch

    glLineWidth(3.0)
    glBegin(GL_LINES)
    # X
    glColor3f(1.0, 0.0, 0.0) # Red

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(2.0, 0.0, 0.0)

    # arrow
    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(1.5, 0.5, 0.0)

    glVertex3f(2.0, 0.0, 0.0)
    glVertex3f(1.5, -0.5, 0.0)

    # Y
    glColor3f(1.0, 1.0, 1.0) # White

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 2.0, 0.0)

    # arrow
    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(0.5, 1.5, 0.0)

    glVertex3f(0.0, 2.0, 0.0)
    glVertex3f(-0.5, 1.5, 0.0)

    # Z
    glColor3f(0.0, 0.0, 1.0) # Blue

    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 2.0)

    # arrow
    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.0, 0.5, 1.5)

    glVertex3f(0.0, 0.0, 2.0)
    glVertex3f(0.0, -0.5, 1.5)
    glEnd()

         
def read_data():
    global ax, ay, az
    ax = ay = az = 0.0
    line_done = 0

    # request data by sending a dot
    ser.write(b".") #* encode string to bytes
    #while not line_done:
    line = ser.readline() 
    angles = line.split(b", ")
    if len(angles) == 3:    
        ax = float(angles[0])
        ay = float(angles[1])
        az = float(angles[2])
        line_done = 1 

def main():
    global yaw_mode,record_mode,axis_mode

    video_flags = OPENGL|DOUBLEBUF
    
    pygame.init()
    screen = pygame.display.set_mode((640,480), video_flags)
    pygame.display.set_caption("Press Esc to quit, z toggles yaw mode, s toggles data recording")
    resize(640,480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()  #* quit pygame properly
            break       
        if event.type == KEYDOWN and event.key == K_z:
            yaw_mode = not yaw_mode
            ser.write(b"z")
        read_data()
        
        draw()
        
        if event.type == KEYDOWN and event.key == K_a:
            axis_mode = not axis_mode
            print("Toggle Axes...")

        if axis_mode:
            axes()
        
        if event.type == KEYDOWN and event.key == K_s:
            record_mode = not record_mode
            print("Toggle data recording in CSV...")

        if record_mode:
            storeCsv(ay,ax,az)

        pygame.display.flip()
        frames = frames+1

    print(("fps:  %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks))))
    ser.close()

if __name__ == '__main__': main()

