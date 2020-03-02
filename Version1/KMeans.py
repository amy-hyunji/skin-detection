from sklearn.cluster import KMeans
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import torch

def skin(color):
	temp = np.uint8([[color]])
	color = cv2.cvtColor(temp, cv2.COLOR_RGB2HSV)
	color = color[0][0]
	e8 = (color[0] <= 25) and (color[0] >= 0)
	e9 = (color[1] < 174) and (color[1] > 58)
	e10 = (color[2] <= 255) and (color[2] >= 50)
	return (e8 and e9 and e10)

"""
get average dominant color of "num" number of colors
"""
def get_average_color(hist, centroids, num = 3):
	max_prob = []
	COLOR = []
	index = []
	cindex = -1
	for (percent, color) in zip(hist, centroids):
		cindex += 1
		if (color[0]+color[1]+color[2]<250*3) and (color[0]+color[1]+color[2]>5*3):
			if (len(max_prob) < num):
				max_prob.append(percent)
				COLOR.append(color)
				index.append(cindex)
			else:
				if (percent > min(max_prob)):
					_index = max_prob.index(min(max_prob))
					del COLOR[_index]; del index[_index]; del max_prob[_index]
					max_prob.append(percent); COLOR.append(color); index.append(cindex)

	r = 0.0; g = 0.0; b = 0.0
	for color in COLOR:
		r += color[0]
		g += color[1]
		b += color[2]
	r = r/num; g = g/num; b = b/num
	COLOR = [r, g, b]
	return COLOR, index

"""
get dominant color
"""
def get_color(hist, centroids):
	max_prob = 0
	COLOR = [0, 0, 0]
	for (percent, color) in zip(hist, centroids):
		if (percent > max_prob):
			max_prob = percent
			COLOR = color
	return COLOR

"""
get instance color close to dominant * percent 
"""
"""
def close_bound(image, dominant, percent = 0.8):
	p_dominant = []
	min_diff = 0; min_COLOR = []
	first = True
	for num in dominant: 
		p_dominant.append(num * percent) 
	for color in image:
		diff = 0
		for i in range(3):
			diff += abs(p_dominant[i] - color[i])
		if (first == True):
			min_diff = diff
			min_COLOR = color
			first = False
		elif (min_diff > diff): 
			min_diff = diff
			min_COLOR = color
	return min_COLOR
"""

def close_bound(image, dominant, percent = 0.8):
	image = np.array(image)
	dominant = np.array(dominant)
	dominant = dominant * percent
	diff = abs(image - dominant)
	temp = np.sum(diff, axis=1)
	index = np.argmin(temp)
	min_COLOR = image[index]
	return min_COLOR

"""
return max and min color in centroids
"""
def remove_maxmin(hist, centroids):
	max_COLOR = [0, 0, 0]
	min_COLOR = [0, 0, 0]
	min_sum = 0
	max_sum = 0
	for (percent, color) in zip(hist, centroids):
		color_sum = color[0] + color[1] + color[2]	
		if (min_sum == 0 and max_sum == 0):
			min_sum = color_sum; max_sum = color_sum
			min_COLOR = color; max_COLOR = color
		else:
			if (color_sum > max_sum):
				max_sum = color_sum
				max_COLOR = color
			elif (color_sum < min_sum):
				min_sum = color_sum
				min_COLOR = color
	return min_COLOR, max_COLOR

"""
get histogram of centroid
"""
def centroid_histogram(clt):
	numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
	(hist, _) = np.histogram(clt.labels_, bins=numLabels)
	hist = hist.astype("float")
	hist /= hist.sum()
	return hist

def get_bound_color (result, skin_color, lower, param, mode):
	if (mode == "RGB"): 
		skin_temp2 = np.uint8([[skin_color]])
		skin_color = cv2.cvtColor(skin_temp2, cv2.COLOR_HSV2RGB)
		skin_color = skin_color[0][0]
	if (lower == False): bound = close_bound(result, skin_color, 1 + param)
	else: bound = close_bound(result, skin_color, 1 - param)
	if (mode == "RGB"):
		bound_color = np.uint8([[bound]])
		bound_color = cv2.cvtColor(bound_color, cv2.COLOR_RGB2HSV)
		bound_color = bound_color[0][0]
		bound_color = np.uint16(bound_color)
	else:
		bound_color = np.uint16(bound)
	return bound_color

def get_skin_color(img_file, seg_file, mode, remove_max_min=False, cluternum=4):
#	img = Image.open(img_file).convert('RGB')
	img = cv2.imread(img_file)
	if (mode == "HSV"): 
		_temp = np.uint8(img)
		_temp = cv2.cvtColor(_temp, cv2.COLOR_BGR2HSV)
		img = np.int16(_temp)
	elif (mode == "RGB"):
		_temp = np.uint8(img)
		_temp = cv2.cvtColor(_temp, cv2.COLOR_BGR2RGB)
		img = np.int16(_temp)	

	seg = Image.open(seg_file)
	parse_array = np.array(seg)
	shape = (parse_array > 0).astype(np.float32)
	head = (parse_array == 4).astype(np.float32) + (parse_array == 13).astype(np.float32)
	print("shape of head:{}, shape of img: {}".format(head.shape, img.shape))
	result = np.array(img)[head.astype(bool)]

	clt = KMeans(n_clusters = cluternum)
	clt.fit(result)
	centroids = clt.cluster_centers_
	hist = centroid_histogram(clt)

#result = np.concatenate([centroids, result], 0)
	
	if (remove_max_min):
		labels = clt.labels_
		min_COLOR, max_COLOR = remove_maxmin(hist, centroids)
		min_label = np.where(centroids == min_COLOR)
		max_label = np.where(centroids == max_COLOR)
		result = result[np.logical_and((labels != min_label),(labels != max_label))]
		_shape = result.shape
		result = result.reshape((_shape[1], _shape[2]))

		clt = KMeans(n_clusters = int(cluternum/2))
		clt.fit(result)
		centroids = clt.cluster_centers_
		hist = centroid_histogram(clt)

	skin_color = get_color(hist, centroids)
	if (mode == "RGB"):
		skin_temp2 = np.uint8([[skin_color]])
		skin_color = cv2.cvtColor(skin_temp2, cv2.COLOR_RGB2HSV)
		skin_color = skin_color[0][0]
		skin_color = np.int16(skin_color)
	if (mode == "HSV"):
		skin_color = np.uint16(skin_color)
	return skin_color, result

