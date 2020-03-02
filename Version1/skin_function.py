from change import change_skin
from KMeans import get_skin_color, get_bound_color
from utils import *
import cv2
import numpy as np
import argparse
import sys


def change_skin(src, tar, srcseg, tarseg, save_path, mode = "RGB", which = "image"):

	if (which != "color" or which != "image"):
		print("value of which should be either [color] or [image]")
		sys.exit()
	if (mode != "HSV" or mode != "RGB"):
		print("value of mode should be either [HSV] or [RGB]")
		sys.exit()

	with open(src,'rb') as inputImage:
		if(which=="color"):
			a=tar.strip('[] ')
			b=a.split(',')
			tar_color = [int(b[0].strip()), int(b[1].strip()), int(b[2].strip())]
		elif(which=="image"):
			tar_color, result = get_skin_color(tar, tarseg, mode) 
			src_color, _ = get_skin_color(src, srcseg, mode)
			param, lower = get_param(tar_color, src_color)
			tar_color = get_bound_color(result, tar_color, lower, param, mode)
		else:
			print("Please enter correct detection type. Should be [image] or [color]")
			sys.exit()
		result = change_skin(inputImage, tar_color, src, srcseg, mode)
	return result
