import argparse
import os
import sys
from cv2 import cv2 as cv

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)

# from pytracking.evaluation import Tracker, get_dataset
# from pytracking.evaluation.running import run_dataset


def get_image_list(image_path, image_type):
    """[summary]

    :param image_path: [description]
    :type image_path: [type]
    :param image_type: [description]
    :type image_type: [type]
    :return: [description]
    :rtype: [type]
    """    
    image_list = []
    for filename in os.listdir(image_path):
        if filename.endswith(image_type):
            image_list.append(filename)

    image_list.sort()
    return image_list


def convert_images_to_video(image_path, video_path, fps=30.0, frameSize=None, image_type='jpg'):
    """[summary]

    :param image_path: [description]
    :type image_path: [type]
    :param video_path: [description]
    :type video_path: [type]
    :param fps: [description], defaults to 30.0
    :type fps: float, optional
    :param frameSize: [description], defaults to None
    :type frameSize: [type], optional
    :param image_type: string, defaults to 'jpg'
    :type image_type: str, optional
    """
    image_list = get_image_list(image_path, image_type)
    if not len(image_list): return

    if not frameSize:
        image = cv.imread(image_list[0])
        height, width, _ = image.shape
        frameSize = (width, height)
    
    video = cv.VideoWriter(video_path, fourcc=-1, fps=fps, frameSize=frameSize)
    for image_name in image_list:
        image = cv.imread(image_name)
        video.write(image)

    cv.destroyAllWindows()
    video.release()


def main():
    parser = argparse.ArgumentParser(description='Run converter from images to videos.')
    
    args = parser.parse_args()

    try:
        seq_name = int(args.sequence)
    except:
        seq_name = args.sequence

    

if __name__ == '__main__':
    main()