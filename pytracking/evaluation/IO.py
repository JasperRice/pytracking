from cv2 import cv2 as cv

def save_image(bbox, in_path, out_path, show=False, color=(0, 255, 0), thickness=2):
    """[summary]

    :param bbox: [description]
    :type bbox: [type]
    :param in_path: [description]
    :type in_path: [type]
    :param out_path: [description]
    :type out_path: [type]
    :param show: [description], defaults to False
    :type show: bool, optional
    :param color: the color of the bounding box, defaults to (0, 255, 0)
    :type color: tuple, optional
    :param thickness: the thickness of the bounding box, defaults to 2
    :type thickness: int, optional
    """
    left_corner = (bbox[0], bbox[1])
    right_corner = (left_corner[0] + bbox[2], left_corner[1] + bbox[3])

    image = cv.imread(in_path)
    image = cv.rectangle(image, left_corner, right_corner, color, thickness, None, None)
    cv.imwrite(out_path, image)
    if show: cv.imshow('Image', image)

def save_video():
    pass