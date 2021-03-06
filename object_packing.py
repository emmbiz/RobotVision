# USAGE
# python object_packing.py --image images/objects.png

# Import the necessary packages
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
from rectpack import newPacker
import numpy as np
from numpy import array
import argparse
import imutils
import cv2
import math
import socket
import time

# Measure the size of objects in an image
def midpoint(ptA, ptB):
    return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# Construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image",
                help="path to the input image")
args = vars(ap.parse_args())

# Load the image, convert it to grayscale, and blur it slightly
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.GaussianBlur(gray, (7, 7), 0)

cv2.imshow('gray', gray)
cv2.waitKey()

# Perform edge detection, then perform dilation + erosion to
# close gaps in between object edges
edged = cv2.Canny(gray, 50, 100)
edged = cv2.dilate(edged, None, iterations=1)
edged = cv2.erode(edged, None, iterations=1)

cv2.imshow('edged', edged)
cv2.waitKey()

# Find contours in the edge map
cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)

cnts = imutils.grab_contours(cnts)

# Sort the contours from left-to-right and initialize the
# 'pixels per metric' calibration variable
(cnts, _) = contours.sort_contours(cnts)
pixelsPerMetric = 9
store1 = []
store2 = []
centerP = []

# Loop over the contours individually
for c in cnts:
    # If the contour is not sufficiently large, ignore it
    if cv2.contourArea(c) < 100:
        continue

    # Compute the rotated bounding box of the contour
    orig = image.copy()
    box = cv2.minAreaRect(c)
    box = cv2.boxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
    box = np.array(box, dtype="int")

    # Order the points in the contour such that they appear
    # in top-left, top-right, bottom-right, and bottom-left
    # order, then draw the outline of the rotated bounding
    # box
    box = perspective.order_points(box)
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)

    # Loop over the original points and draw them
    for (x, y) in box:
        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

    # Unpack the ordered bounding box, then compute the mid-point
    # between the top-left and top-right coordinates, followed by
    # the mid-point between bottom-left and bottom-right coordinates
    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)

    # Compute the mid-point between the top-left and bottom-right points,
    # followed by the mid-point between the top-right and bottom-right
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)

    # Draw the mid-points on the image
    cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)

    # Draw lines between the mid-points
    cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
             (255, 0, 255), 2)
    cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
             (255, 0, 255), 2)

    # Compute angle at which to pick up object
    angle = int(math.atan((-tlblY + trbrY) / (trbrX - tlblX)) * 180 / math.pi)

    # Find mid-point of the bounding box for picking object
    (pickX, pickY) = midpoint(tl, br)
    centerP.append([pickX, pickY, angle])

    # Compute the Euclidean distance between the mid-points
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))

    if dB >= dA:
        angle = angle + 90
    print('Angle = ', angle) ##

    # Compute the size of the object
    dimA = dA / pixelsPerMetric
    dimB = dB / pixelsPerMetric

    # Store values in an array for further processing
    store1.append(dimA)
    store2.append(dimB)

    # Draw the object sizes on the image
    cv2.putText(orig, "{:.1f}in".format(dimA),
                (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)
    cv2.putText(orig, "{:.1f}in".format(dimB),
                (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (255, 255, 255), 2)

    # Show the output image
    cv2.imshow("Image", orig)
    cv2.waitKey(0)

centerP = array(centerP)

print("Pick point and angle")
print(centerP)

store = []
rid = []
rectangles = []
for m in range(len(store1)):
    rid.append(m)
for n in range(len(store1)):
    rectangles.append([store2[n], store1[n], rid[n]])

for i in rectangles:
    print(i)

##################################################################
# Bin packing algorithm
bins = [(25, 25, 5)]

packer = newPacker()

# Add the rectangles to packing queue
for r in rectangles:
    packer.add_rect(*r)

# Add the bins where the rectangles will be placed
for b in bins:
    packer.add_bin(*b)

# Start packing
packer.pack()

# Obtain number of bins used for packing
nbins = len(packer)

# Index first bin
abin = packer[0]

# Bin dimensions (bins can be reordered during packing)
width, height = abin.width, abin.height

# Number of rectangles packed into first bin
nrect = len(packer[0])

# Second bin first rectangle
rect = packer[0][0]

# rect is a Rectangle object
x = rect.x  # rectangle bottom-left x coordinate
y = rect.y  # rectangle bottom-left y coordinate
w = rect.width
h = rect.height

ind = []
rectfinal = []
all_rects = packer.rect_list()
for rect in all_rects:
    # print(rect)
    b, x, y, w, h, rid = rect
    ind.append(rid)
    rectfinal.append(rect)
print(type(rectfinal))
rectfinal = array(rectfinal)
print(rectfinal)
print(type(rectfinal))

# ID sequence after computing
print(ind)

# Visualize bin packing
rectsim = rectfinal.astype(int)
sim = np.zeros((100, 100, 3), np.uint8)
for i in range(len(rectsim)):
    c = 4 * int(rectsim[i][1] + rectsim[i][3])
    d = 4 * int(rectfinal[i][2] + rectfinal[i][4])
    cv2.rectangle(sim, (4 * int(rectfinal[i][1]), 4 * int(rectfinal[i][2])), (c, d), (0, 255, 0), 3)
    cv2.imshow('sim', sim)
    cv2.waitKey()

# Create a list of final packed bin with angle
fp = []
for i in range(len(rectangles)):
    for j in range(len(rectfinal)):
        if rectangles[i][2] == rectfinal[j][5]:
            if rectangles[i][0] == rectfinal[j][3]:
                print(' %2.1f not rotated', (rectangles[i][2]))
                fp.append([rectangles[i][0], rectangles[i][1], 0])
            else:
                print(' %2.1f  rotated', (rectangles[i][2]))
                fp.append([rectangles[i][0], rectangles[i][1], 90])

print('length    height    angles')
for i in range(len(rectangles)):
    print("{:6f}    {:6f}   {:6f}".format(fp[i][0], fp[i][1], fp[i][2]))

# Check for rotation
fl = []
for i in range(len(rectfinal)):
    for j in range(len(rectangles)):
        if rectfinal[i][5] == rectangles[j][2]:
            if rectfinal[i][3] == rectangles[j][0]:
                print('not rotated', (rectfinal[i][5]))
                fl.append([rectfinal[i][3], rectfinal[i][4], 0])
            else:
                print('rotated', (rectfinal[i][5]))
                fl.append([rectfinal[i][3], rectfinal[i][4], 90])

print('drop X    drop y   angles     length     height')
for i in range(len(rectfinal)):
    print("{:6f}    {:6f}    {:6f}    {:6f}    {:6f}".format(rectfinal[i][1] + (rectfinal[i][3]) / 2,
                                                             rectfinal[i][2] + (rectfinal[i][4]) / 2, fl[i][2],
                                                             fl[i][0], fl[i][1]))

########################################################################

# Initialize socket connection with UR5
HOST = "192.168.56.102"  # The remote host
PORT = 30000  # The same port as used by the server
print("Starting Program")
count = 0

while (count < 1000):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))  # Bind to the port
    s.listen(5)  # Now wait for client connection.
    c, addr = s.accept()  # Establish connection with client.
    try:

        for i in range(len(centerP)):
            msg = str(c.recv(1024), 'utf-8')
            print("Request = ", msg)
            msg = str(c.recv(1024), 'utf-8')
            print("Request = ", msg)
            # time.sleep(0.5)
            msg = str(c.recv(1024), 'utf-8')
            print("Request = ", msg)
            if msg == "asking_for_data":
                print("(%3i,%3i,%3i)" % (centerP[i][0], centerP[i][1], centerP[i][2]))
                c.send(b'(%3i,%3i,%3i)' % (int(centerP[i][0]), int(centerP[i][1]), int(centerP[i][2])))

            msg = str(c.recv(1024), 'utf-8')
            print("Request = ", msg)
            # time.sleep(1)
            if msg == "asking_for_drop_point":
                c.send(b'(%3i,%3i,%3i)' % (
                rectfinal[i][1] + (rectfinal[i][3]) / 2, rectfinal[i][2] + (rectfinal[i][4]) / 2, fl[i][2]))
                print("sent (%3i,%3i,%3i) " % (
                rectfinal[i][1] + (rectfinal[i][3]) / 2, rectfinal[i][2] + (rectfinal[i][4]) / 2, fl[i][2]))

    except socket.error as socketerror:
        print(count)

c.close()
s.close()
print("Program finish")
