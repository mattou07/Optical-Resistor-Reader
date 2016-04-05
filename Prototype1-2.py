import cv2
import numpy as np
from PIL import Image
import Tkinter, tkFileDialog
#Problems:
#RGB may not be the best colour space to use
#Need to address vertical scan giving up when there is 1 black pixel in the way of a white pixel

#Some false edges may be detected close together consecutively without being real edges
#due to brightness etc. Possibly make a rule where if lots of edges are found in a small area
#shows that they are not valid edges

#Using Tkinter to get the user to load any image they want
root = Tkinter.Tk()
root.withdraw()
#http://stackoverflow.com/questions/9319317/quick-and-easy-file-dialog-in-python
picfile = tkFileDialog.askopenfilename()
thickness = 1  #debug line thickness
# Sites to look at
# http://stackoverflow.com/questions/11064786/get-pixels-rgb-using-pil

# This build is going to be the first colour prototype
# Program is capable of marking edges to a decent accuracy

# The program works like this
# We set our global variables
#  loop is used as
# a break for the picture display loop
#
# Get mouse will just return the x and y coordinates for a given mouse click
# and will stop the loop when the mouse is clicked 4 times
#
# We then read in our image file and create a binary image with edges marked out
#
# Next the processed binary image is opened with PIL (Python Imaging Library)
#
# The program next loads the image on the screen and runs the mouse
# function every time the mouse is clicked
#
# The coordinates are put into a stack and then emptied into an array
#
# We find the average of the line with the two Y coords provided so we get a straight line
#
# Lines are then drawn on the binary image so the user can see what parts of the image
# the computer is scanning
#
# The other 2 clicks are for the height of the resistor
#
# Image is then opened into memory to prepare for the pixel scanning operations
# For loop is explained lower down


#Mouse coord function
global loop, c, bounds
loop = True
c=0
bounds = []

def get_mouse(event,x,y,flags,param):
    global ix,iy,drawing,mode, loop, c, bounds

    if event == cv2.EVENT_LBUTTONDOWN:
        c=c+1
        ix,iy = x,y
        print "Position x="
        print ix
        print"y="
        print iy
        bounds.append([ix,iy])
        if c == 4:
            loop = False

def calculatecolour(colourlist):
    coloursize= len(colourlist)
    r = 0
    g = 0
    b = 0
    for i in colourlist:
        r+=i[0]
        g+=i[1]
        b+=i[2]

    return [r/coloursize, g/coloursize, b/coloursize]

def getbackgroundcolour(x,y,rgb_im,Markedimg):
    #Function is used to get the average of a background colour
    #For a given area
    #This could be a band or the background of the resistor
    colourbackarray = []
    #Scan in rectangles
    #Collect lots of pixels
    for scanx in range (x-2,x+2):

        for scan in range(y,y+10):
            cv2.line(Markedimg,(scanx,scan),(scanx,scan),(255,255,0),thickness)
            r, g, b = rgb_im.getpixel((scanx,scan))
            colourbackarray.append([r,g,b])

        for scan in range(y,y+10,-1):
            cv2.line(Markedimg,(scanx,scan),(scanx,scan),(255,255,0),thickness)
            r, g, b = rgb_im.getpixel((scanx,scan))
            colourbackarray.append([r,g,b])
    #Then work out the average of all of those colours
    return calculatecolour(colourbackarray)


img = cv2.imread(picfile)
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
#gray = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
edges = cv2.Canny(gray,5,60,apertureSize = 3)


cv2.imwrite('houghlines3.jpg',edges)
edges = Image.open('houghlines3.jpg')
img = cv2.imread('houghlines3.jpg',0)
cv2.imshow('frame', img)
#cv2.waitKey(0)
while(loop):
    cv2.setMouseCallback('frame',get_mouse)

    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
print bounds
leftbound = bounds.pop(0)
rightbound = bounds.pop(0)
upperbound = bounds.pop(0)
lowerbound = bounds.pop(0)

#force y coords from mouse clicks to be the same by adding y1+y2/2
#This allows us to have a straight
averageY=leftbound[1]+rightbound[1]
averageY=averageY/2
print averageY
img = cv2.imread('houghlines3.jpg',0)
##draw x bounds
cv2.line(img,(leftbound[0],averageY),(rightbound[0],averageY),(255,0,0),1)

##draw y bounds
cv2.line(img,(leftbound[0],upperbound[1]),(rightbound[0],upperbound[1]),(255,0,0),1)
cv2.line(img,(leftbound[0],lowerbound[1]),(rightbound[0],lowerbound[1]),(255,0,0),1)
cv2.imwrite('averageY.jpg', img)
#

#img = cv2.imread('houghlines3.jpg',0)
#cv2.line(img,(leftbound[0],leftbound[1]),(rightbound[0],rightbound[1]),(255,0,0),1)

##cv2.imshow('frame', img)
##
##while True:
##    if cv2.waitKey(1) & 0xFF == ord('q'):
##            break
##
##cv2.destroyAllWindows()

imgproper = Image.open(picfile)
print lowerbound[1]
print upperbound[1]
edges = Image.open('houghlines3.jpg')
edgepix = edges.load()
bandbounds = [] #a list of the bounds of each band
spacecount = 0
bandsfound = []
bandsfoundx = []
found = []
inbetween = False #used to reduce long print statements
bandfound = False
print "Begin finding bands"
xdifference = rightbound[0]-leftbound[0]
ydifference = upperbound[1] - lowerbound[1]
#setting Y coord for the top and lower thread
topthread = upperbound[1]-averageY
topthread= averageY+topthread

lowerthread = lowerbound[1]-averageY
lowerthread = averageY+lowerthread

#For loop will go through every pixel in the range of the set x coordinates
# detecthorizontal will contain the RGB value of the selected pixel [x,y]
# Spacecount counts the number of pixels between each edge and resets to 0 when an edge is found
# if statement will run if there is a pixel with an rgb value over 250 (to account for anomalies)
# Once we find a edge when going along the image on the x axis
# We then begin scanning on the Y axis on where the edge was detected
# So poscurrentY will scan up on the y axis while negcurrentY will scan down on the Y axis




InBetweenColourArray  =  [] #this will collect all the colours in between edges
#Which allows us to add them together and get an average of the colour between edges

#Store the colours of bands
colours =[]

#basebool = True

#Open the colour version of image with PIL
colourim = Image.open(picfile)
#Store the image in RGB format
rgb_im = colourim.convert('RGB')
Markedimg = cv2.imread('houghlines3.jpg')
edgecount = 0
counter = 0 #counts how many times we find an edge
#================================================================================================================================
for x in range(leftbound[0],rightbound[0]):
    #spacecount=spacecount+1
    #Store the RGB value of the pixel
    detecthorizontal = edgepix[x,averageY]

    #get the colour to be averaged out
    r, g, b = rgb_im.getpixel((x,averageY))
    InBetweenColourArray.append([r,g,b])


    if detecthorizontal >= 250: ##we detect an edge going along the middle horizontal axis
        print ("=======================================================================================")
        numofwhitespos = 0
        numofwhitesneg = 0
        poscurrentY=averageY
        negcurrentY=averageY
        detectvertical = True
        #count up y axis
        #Scan up and down
        while (detectvertical):
            #print poscurrentY
            #print negcurrentY
            poswhite = edgepix[x,poscurrentY]
            negwhite = edgepix[x,negcurrentY]

            #print "poswhite is " + str(poswhite[0]) +str(poswhite[1])
#================================================================================================================================
            #if we find a white going up
            if poswhite >= 250:
                numofwhitespos = numofwhitespos+1
                #GREEN DEBUG LINE DRAW trace edge scan with a green marker
                cv2.line(Markedimg,(x,poscurrentY),(x,poscurrentY),(0,255,0),thickness) #debug lines

            # otherwise check the pixel on the left or right and see if a white pixel is there (to account for diagonal lines)
            else:
                #check left and right
                #edited
                # If we find a white pixel there then add it to the number of whites
                if edgepix[x-1,poscurrentY]>=250 or edgepix[x+1,poscurrentY]>=250:
                    numofwhitespos = numofwhitespos+1
                    #GREEN DEBUG LINE DRAW trace edge scan with a green marker
                    cv2.line(Markedimg,(x,poscurrentY),(x,poscurrentY),(0,255,0),thickness)

                #otherwise end the loop since its likely to not be a valid edge
                else:
                    detectvertical = False

#================================================================================================================================

            #if we find a white while going down
            if negwhite >= 250:
                numofwhitesneg = numofwhitesneg+1
                #GREEN DEBUG LINE DRAW trace edge scan with a green marker
                cv2.line(Markedimg,(x,negcurrentY),(x,negcurrentY),(0,255,0),thickness)

            # otherwise check the pixel on the left or right and see if a white pixel is there (to account for diagonal lines)
            else:
                #edited
                # If we find a white pixel there then add it to the number of whites
                if edgepix[x-1,negcurrentY]>=250 or edgepix[x+1,negcurrentY]>=250:
                    numofwhitesneg = numofwhitesneg+1
                    #GREEN DEBUG LINE DRAW trace edge scan with a green marker
                    cv2.line(Markedimg,(x,negcurrentY),(x,negcurrentY),(0,255,0),thickness)
                #otherwise end the loop since its likely to not be a valid edge
                else:
                    detectvertical = False
#================================================================================================================================
            poscurrentY= poscurrentY+1
            negcurrentY= negcurrentY-1

        # if we find 3 consecutive whites going up and down then we are likely to have found an edge
        if numofwhitespos > 4 and numofwhitesneg >4:
            if edgecount == 0:
                #colours.append(calculatecolour(colourarray))
                InBetweenColourArray = []


            # Marking where the detected edges are
            #Debug Prints
            counter+=1
            print counter
            print "Average colour is to the left"
            left= getbackgroundcolour(x-5,averageY,rgb_im,Markedimg) #get background colour of before edge detection
            print left
            print "Average colour is to the right"
            right =getbackgroundcolour(x+5,averageY,rgb_im,Markedimg) #get background colour of after edge detection
            print right
            #print "This is the"
            #abs keeps the number positive
            #We find  the difference on one side of the edge and the other
            comparison = [abs(left[0]-right[0]),abs(left[1]-right[1]),abs(left[2]-right[2])]
            print "The difference between the two backgrounds is"
            print comparison
            #BLUE DEBUG LINE DRAW trace colour scan
            cv2.line(Markedimg,(x,averageY),(x,averageY),(255,0,0),thickness+2)
            cv2.line(Markedimg,(x-3,averageY-7),(x-3,averageY-7),(0,0,255),thickness)
            if edgecount==1:
                colours.append(calculatecolour(InBetweenColourArray))
                print colours
                InBetweenColourArray=[]
                edgecount=0



            edgecount+=1
            #print "Edge found currently at {coord}. Number of 255's found at positive blocks {whitefound} and negative blocks {blackfound}".format(whitefound=numofwhitespos,blackfound=numofwhitesneg,coord=x)



print InBetweenColourArray
print "colours are"
print  colours

cv2.imwrite('plottedline.jpg',Markedimg)

#print bandsfound
#bandsfound.sort()
#print bandsfound
#numofbands = raw_input('How many bands are on the resistor?')
#howmanytodelete = len(bandsfound)-int(numofbands)

#for num in range (0,howmanytodelete):
#    bandsfound.pop(0)

#print bandsfound

#print bandsfoundx



#finalcolour = [r/coloursize, g/coloursize, b/coloursize]
#print "final"
#print finalcolour
#work out colour average
#def colouraverage (colourarray):



cv2.imshow('frame', Markedimg)
c=0 #need to find a better timer method
while c<1000:
    c+=1

    if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()











