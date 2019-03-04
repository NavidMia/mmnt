import cv2
import os


path = "./training_images/is_interesting/interesting/"
files = os.listdir(path)
files.sort()
for image_name in files:
    name = path + image_name
    img = cv2.imread(name,1)
    img_resize = cv2.resize(img, (368, 432))
    cv2.imwrite(name, img_resize)
