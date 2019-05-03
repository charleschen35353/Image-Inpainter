# Requirements

PyQt5>=5.8.2
Pillow>=4.1.1 
Numpy
Scipy
Tensorflow 1.9
OpenCv-Python

The applications is developed and test under Ubuntu 16.04.
Modified from https://github.com/shkolovy/simple-photo-editor.


# Pre-requitesites

Please put .pb files in https://drive.google.com/drive/folders/1XUad0lEa1_4EwGJmucZNjGk-yyT8ws-O?usp=sharing into models/

# User Guide

run $python photo_editor.py 

To start with, simply click on "upload" button.

Once the image is uploaded, one can apply filters under "Filter" Tab.

One can resize images under "Modicfication" Tab.

Once can adjust contrast, birghtness and sharpness under "Adjust" Tab.

To use segmentation, simply click on the "One-tap Segmentation button" under "Character Extraction" Tab. All foreground objects will be removed.

To use imaga matting, under "Character Extraction" Tab, adjust the pen size, and check the box for white(foreground)/ black(backgbround) and mark roughly on the image. Once scribbles are added, click on "Apply Matting" button to extract individual foregrounds. If one wish not to accidentally paint on the image, click on "Disable Drawing".

To apply inpainting, at least one operation on either "Segmentation" or "Image Matting" is supposed to be done. Two inpainting methods are provided here. To execute exemplar inpainting, under "Inpainting" Tab, adjust the slide bars for related parameters and click on exemplar inpainting button. It will take a time for finishing execution. During the execution period, users are NOT suggested to interrupt the process if one wish to keep the inpainting image. 

Also, a quicker inpainting method is provided. One Can click on "Quick Inpainting" under "Inpainting" tab. An restored image will be shown soon.

To change the image one wish to edit, click on "Upload" again and repeat the above steps.

To discard change, click on "Reset" button.
