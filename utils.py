import cv2

def binarization(gray,key):
    ret, gray = cv2.threshold(gray, key, 255, cv2.THRESH_BINARY)
    gray = cv2.fastNlMeansDenoising(gray)
    return gray