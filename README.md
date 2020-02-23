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


# segmentation
- get segmentation image from LIP_JPPNet
- checkpoint dir : https://drive.google.com/open?id=1uyariG-FhkVtXjUagZbWW0uc4jp8Go9m
    - download checkpoint and save in segmentation/checkpoint

usage: main.py [-h] [--data_dir DATA_DIR] [--save_dir SAVE_DIR]
               [--checkpoint_dir CHECKPOINT_DIR] [--steps STEPS]
               [--width WIDTH] [--height HEIGHT]

optional arguments:
  -h, --help            show this help message and exit
  --data_dir DATA_DIR   directory of data
  --save_dir SAVE_DIR   directory of data
  --checkpoint_dir CHECKPOINT_DIR
                        directory of checkpoint
  --steps STEPS         number of images
  --width WIDTH         width size of image
  --height HEIGHT       height size of image
