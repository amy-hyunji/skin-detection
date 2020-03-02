import numpy as np
import cv2
import sys
from KMeans import get_skin_color

MODE = "RGB"
# MODE = "HSV"

def skinRange(H,S,V):
	e8 = (H<=25) and (H>=0)
	e9 = (S<174) and (S>58)
	e10 = (V<=255) and (V>=50)
	return (e8 and e9 and e10)

def doDiff (img, tar_color, skin_color, size):
	print("tar color: {}, skin_color: {}".format(tar_color, skin_color))
	for i in range(3):
		_img = img[:, :, i]
		tar = tar_color[i]
		src = skin_color[i]
		_img = np.reshape(_img, (_img.shape[0] * _img.shape[1], 1))
		_img[_img < src] = _img[_img<src] * tar / src 
		_img[_img > src] = tar + ((255-tar)*(_img[_img>src]-src) / (255-src))
		_img[_img >= 255] = 255
	print(img.shape)

def make_lower_upper(skin_color,Hue,Saturation,Value):
	if(skin_color[0]>Hue):
		if(skin_color[0]>(180-Hue)):
			if(skin_color[1]>Saturation+10):
				lower1=np.array([skin_color[0]-Hue, skin_color[1]-Saturation,Value], dtype = "uint8")
				upper1=np.array([180, 255,255], dtype = "uint8")
				lower2=np.array([0, skin_color[1]-Saturation,Value], dtype = "uint8")
				upper2=np.array([(skin_color[0]+Hue)%180, 255,255], dtype = "uint8")
				return (True,lower1,upper1,lower2,upper2)
			else:
				lower1=np.array([skin_color[0]-Hue, 10,Value], dtype = "uint8")
				upper1=np.array([180, 255,255], dtype = "uint8")
				lower2=np.array([0, 10,Value], dtype = "uint8")
				upper2=np.array([(skin_color[0]+Hue)%180, 255,255], dtype = "uint8")
				return (True,lower1,upper1,lower2,upper2)
		else:
			if(skin_color[1]>Saturation+10):
				lower=np.array([skin_color[0]-Hue, skin_color[1]-Saturation,Value], dtype = "uint8")
				upper=np.array([skin_color[0]+Hue, 255,255], dtype = "uint8")
				return (False,lower,upper)
			else:
				lower=np.array([skin_color[0]-Hue, 10,Value], dtype = "uint8")
				upper=np.array([skin_color[0]+Hue, 255,255], dtype = "uint8")
				return (False,lower,upper)
	else:
		if(skin_color[1]>Saturation+10):
				lower1=np.array([0, skin_color[1]-Saturation,Value], dtype = "uint8")
				upper1=np.array([skin_color[0]+Hue, 255,255], dtype = "uint8")
				lower2=np.array([180-Hue+skin_color[0], skin_color[1]-Saturation,Value], dtype = "uint8")
				upper2=np.array([180, 255,255], dtype = "uint8")
				return (True,lower1,upper1,lower2,upper2)
		else:
			lower1=np.array([0, 10,Value], dtype = "uint8")
			upper1=np.array([skin_color[0]+Hue, 255,255], dtype = "uint8")
			lower2=np.array([180-Hue+skin_color[0], 10,Value], dtype = "uint8")
			upper2=np.array([180, 255,255], dtype = "uint8")
			return (True,lower1,upper1,lower2,upper2)

def change_skin(image_file, tar_color, img_path, seg_path, mode): 

	if(isinstance(image_file,str)):
		img=cv2.imread(image_file,1)
	else:
		img=cv2.imdecode(np.fromstring(image_file.read(), np.uint8),1)
	hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	rgb_img=np.float32(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
	size=img.shape

	skin_color, _ = get_skin_color(img_path, seg_path, mode) # HSV

#	if(skinRange(skin_color[hsvskin_color[1],skin_color[2])): 
	Hue=10
	Saturation=65
	Value=50
	result=make_lower_upper(skin_color,Hue,Saturation,Value)
	if(result[0]):
		lower1=result[1]
		upper1=result[2]
		lower2=result[3]
		upper2=result[4] 
		skinMask1=cv2.inRange(hsv_img, lower1, upper1)
		skinMask2=cv2.inRange(hsv_img, lower2, upper2)
		skinMask=cv2.bitwise_or(skinMask1,skinMask2)
	else:
		lower=result[1]
		upper=result[2]
		skinMask = cv2.inRange(hsv_img, lower, upper)
	
	skinMaskInv=cv2.bitwise_not(skinMask)

	_skin_color = np.uint8([[skin_color]])
	_skin_color = cv2.cvtColor(_skin_color,cv2.COLOR_HSV2RGB)
	_skin_color=_skin_color[0][0] # RGB
	_skin_color=np.int16(_skin_color)

	_tar_color = np.uint8([[tar_color]])
	_tar_color = cv2.cvtColor(_tar_color, cv2.COLOR_HSV2RGB)
	_tar_color = _tar_color[0][0]
	_tar_color=np.int16(_tar_color) 

	# Change the color maintaining the texture.
	if (MODE == "HSV"):
		doDiff(hsv_img, tar_color, skin_color, size)
		img2 = np.uint8(hsv_img)
		img2 = cv2.cvtColor(img2, cv2.COLOR_HSV2BGR)
	elif (MODE == "RGB"):
		doDiff(rgb_img, _tar_color, _skin_color, size)
		img2 = np.uint8(rgb_img)
		img2 = cv2.cvtColor(img2, cv2.COLOR_RGB2BGR)


	# Get the two images ie. the skin and the background.
	imgLeft=cv2.bitwise_and(img,img,mask=skinMaskInv)
	skinOver = cv2.bitwise_and(img2, img2, mask = skinMask)
	skin = cv2.add(imgLeft,skinOver)

	res=cv2.imencode('.jpg',skin)[1].tostring()
	return res
	
