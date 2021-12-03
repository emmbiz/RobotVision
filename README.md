# RobotVision
This is an implementation of a 2D packing system by integrating a vision system (Raspberry Pi 3 and Camera Module V2) to a UR5 robot arm manipulator for effective and efficient packing solution of multiple shaped objects without human intervention.

The implementation steps involves:-
1. Determining the shape, size, angle and location of objects for packing.
2. Solving the 2D bin packing problem to find the optimal packing solution.
3. Transmitting data for communication between Raspberry Pi and UR5 robot.
4. Executing commands based on data received to pick and place objects to desired location.



[![Watch the video](https://user-images.githubusercontent.com/87937713/144323725-0295c31e-b7c1-4390-bedd-d2d928fe9a95.PNG)](https://youtu.be/pxScDC5OCfo)



# References
- https://www.pyimagesearch.com/2016/03/28/measuring-size-of-objects-in-an-image-with-opencv/
- https://www.pyimagesearch.com/2016/02/01/opencv-center-of-contour/
- https://www.universal-robots.com/how-tos-and-faqs/how-to/ur-how-tos/moving-to-a-position-calculated-from-user-input-16605
