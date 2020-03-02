from change import change_skin
from KMeans import get_skin_color, get_bound_color
from utils import *
import cv2
import numpy as np
import argparse
import sys

if __name__ == "__main__": 
	parser=argparse.ArgumentParser()
	parser.add_argument("--which", default = "image", help="Color Change or Skin Match? (image, color)")
	parser.add_argument("--src", default = "/home/fashionteam/underwear/image/MAN1_0.jpg", help="Image to be changed")
	parser.add_argument("--tar", default = "/home/fashionteam/underwear/image/WOMEN1_0.jpg", help="Required skin color or the OTHER image")
	parser.add_argument("--srcseg", default = "/home/fashionteam/underwear/image-parse/MAN1_0.png", help="path for segmentation of input image")
	parser.add_argument("--tarseg", default = "/home/fashionteam/underwear/image-parse/WOMEN1_0.png", help="path for segmentation of color image")
	parser.add_argument("--save", default = "./temp", help="Path where image is to be saved")
	parser.add_argument("--mode", default = "HSV", help="mode to cluster color: (HSV / RGB)")
	args=parser.parse_args()

	with open(args.src,'rb') as inputImage:
		if(args.which=="color"):
			a=args.col.strip('[] ')
			b=a.split(',')
			tar_color = [int(b[0].strip()), int(b[1].strip()), int(b[2].strip())]
		elif(args.which=="image"):
			tar_color, result = get_skin_color(args.tar, args.tarseg, args.mode) 
			src_color, _ = get_skin_color(args.src, args.srcseg, args.mode)
			param, lower = get_param(tar_color, src_color)
			tar_color = get_bound_color(result, tar_color, lower, param, args.mode)
		else:
			print("Please enter correct detection type. Should be [image] or [color]")
			sys.exit()
		result = change_skin(inputImage, tar_color, args.src, args.srcseg, args.mode)

	with open(args.save,'wb') as resultFile:
		resultFile.write(result)
