from change import change_skin
from KMeans import get_skin_color
import cv2
import numpy as np
import argparse

def get_param(tar, src):
	diff = 0
	compare = 0
	lower = True
	
	for i in range(3):
		_diff = tar[i] - src[i]
		compare += _diff
		diff += abs(_diff)

	if (diff <= 100): param = 0.0
	elif (diff >= 300): param = 0.2
	else: param = (diff - 100) / 200 * 0.2

	if (compare < 0): lower = True
	else: lower = False

	return param, lower


if __name__ == "__main__": 
	parser=argparse.ArgumentParser()
	parser.add_argument("--which", default = "image", help="Color Change or Skin Match? (image, color)")
	parser.add_argument("--src", help="Image to be changed")
	parser.add_argument("--tar", help="Required skin color or the OTHER image")
	parser.add_argument("--srcseg", help="path for segmentation of input image")
	parser.add_argument("--tarseg", help="path for segmentation of color image")
	parser.add_argument("--save", help="Path where image is to be saved")
	parser.add_argument("--mode", default = "HSV", help="mode to cluster color: (HSV / RGB)")
	args=parser.parse_args()

	with open(args.src,'rb') as inputImage:
		if(args.which=="color"):
			a=args.col.strip('[] ')
			b=a.split(',')
			tar_color = [int(b[0].strip()), int(b[1].strip()), int(b[2].strip())]
		elif(args.which=="image"):
			tar_color, _ = get_skin_color(args.tar, args.tarseg, args.mode) 
		else:
			print("Please enter correct detection type.")
		src_color, result = get_skin_color(src, srcseg, args.mode)
		param, lower = get_param(tar_color, src_color)
		bound_color = get_bound_color(result, tar_color, lower, param, args.mode)
		result = change_skin(inputImage, bound_color, args.src, args.srcseg, args.mode)

	with open(args.save,'wb') as resultFile:
		resultFile.write(result)
