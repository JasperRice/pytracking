import argparse
import os
import sys
from cv2 import cv2 as cv

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)


def get_image_list(image_path, image_type):
    """Get all the path of the images in a certain folder

    :param image_path: the folder containing images
    :type image_path: str
    :param image_type: the extension of the images to be searched
    :type image_type: str
    :return: a list of image paths
    :rtype: list
    """
    image_list = []
    for filename in os.listdir(image_path):
        if filename.endswith(image_type):
            image_list.append(os.path.join(image_path, filename))

    image_list.sort()
    return image_list


def convert_images_to_video(image_path, video_path, fps=30.0, frameSize=None, image_type='jpg'):
    """[summary]

    :param image_path: the folder containing images
    :type image_path: str
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

    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    video = cv.VideoWriter(video_path, fourcc=fourcc, fps=fps, frameSize=frameSize)
    for image_name in image_list:
        image = cv.imread(image_name)
        video.write(image)

    video.release()
    cv.destroyAllWindows()


def overlap_bbox_on_video(bbox_path, video_path, out_path=None, gt_path=None, fps=30.0):
    """[summary]

    :param bbox_path: [description]
    :type bbox_path: [type]
    :param video_path: [description]
    :type video_path: [type]
    :param out_path: [description], defaults to None
    :type out_path: [type], optional
    """    
    if not out_path:
        video_path_split = video_path.split('.')
        video_path_split[-2] += "+BBox"
        out_path = '.'.join(video_path_split)
        out_path = out_path.replace('mp4', 'avi')

    bbox_file = open(bbox_path)
    bbox_lines = bbox_file.readlines()

    video = cv.VideoCapture(video_path)
    ret, frame = video.read()

    height, width, _ = frame.shape
    frameSize = (width, height)

    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    output = cv.VideoWriter(out_path, fourcc=fourcc, fps=fps, frameSize=frameSize)

    for i, line in enumerate(bbox_lines):
        if i != 0:
            ret, frame = video.read()

        l, b, w, h = tuple(map(int, line.split()))
        left_corner, right_corner = (l, b), (l+w, b+h)

        frame_bbox = cv.rectangle(frame, left_corner, right_corner, color=(0, 255, 0), thickness=2)
        output.write(frame_bbox)

    bbox_file.close()
    video.release()
    output.release()
    cv.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(description='Run converter from images to videos.')
    parser.add_argument('--tracker_name', type=str, default='dimp',help='Name of tracking method.')
    parser.add_argument('--tracker_param', type=str, default='dimp50', help='Name of parameter file.')
    parser.add_argument('--create_method', type=str, default='image2video', help='Name of the video generation method.')

    args = parser.parse_args()

    # try:
    #     seq_name = int(args.sequence)
    # except:
    #     seq_name = args.sequence

    if args.create_method == 'image2video':
        tracking_results_path = "/home/sifan/Documents/Zhang/pytracking/pytracking/tracking_results"
        tracking_results_path += "/" + args.tracker_name
        tracking_results_path += "/" + args.tracker_param

        file_list = os.listdir(tracking_results_path)
        file_list.sort()

        for i, filename in enumerate(file_list):
            if os.path.isfile(os.path.join(tracking_results_path, filename)):
                del file_list[i]

        path_list = list(map(lambda x: os.path.join(tracking_results_path, x), file_list))

        for file, path in zip(file_list, path_list):
            convert_images_to_video(path, path+'/'+file+'.avi', fps=30.0, frameSize=None, image_type='jpg')
    elif  args.create_method == 'bbox2video':
        bbox_path = '/home/sifan/Documents/pytracking/pytracking/tracking_results/dimp/dimp50/video_Office_001_960x540.txt'
        video_path = '/home/sifan/Documents/pytracking/pytracking/datasets/Videos/Office/Office_001_960x540.mp4'
        overlap_bbox_on_video(bbox_path, video_path)

if __name__ == '__main__':
    main()