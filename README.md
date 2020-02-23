# skin-detection
change the color of skin by other image or specific color


usage: main.py [-h] [--which WHICH] [--src SRC] [--tar TAR] [--srcseg SRCSEG]
               [--tarseg TARSEG] [--save SAVE] [--mode MODE]

optional arguments:
  -h, --help       show this help message and exit
  --which WHICH    Color Change(color) or Skin Match(image)? (image, color)
  --src SRC        Image to be changed
  --tar TAR        Required skin color or the OTHER image (if which == color: [R,G,B] else: image path)
  --srcseg SRCSEG  path for segmentation of input image
  --tarseg TARSEG  path for segmentation of color image
  --save SAVE      Path where image is to be saved
  --mode MODE      mode to cluster color: (HSV / RGB)
