import argparse
import os
import pdb
import sys

import numpy as np
from cv2 import cv2 as cv

env_path = os.path.join(os.path.dirname(__file__), '..')
if env_path not in sys.path:
    sys.path.append(env_path)


_bbox_colors = {
    'normal': (0, 255, 0),
    'uncertain': (0, 255, 255),
    'hard_negative': (255, 0, 0),
    'not_found': (0, 0, 255),
    'search': (127, 127, 127)
}


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
    if not len(image_list):
        return
    if not frameSize:
        image = cv.imread(image_list[0])
        height, width, _ = image.shape
        frameSize = (width, height)

    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    video = cv.VideoWriter(video_path, fourcc=fourcc,
                           fps=fps, frameSize=frameSize)
    for image_name in image_list:
        image = cv.imread(image_name)
        video.write(image)

    video.release()
    cv.destroyAllWindows()


def rotate_video(video_path, rotate_angle, scale=1.0, out_path=None, fps=30.0):
    if out_path in [None, '']:
        video_path_split = video_path.split('.')
        video_path_split[-2] += '+Rotated'
        out_path = '.'.join(video_path_split)
    video = cv.VideoCapture(video_path)
    ret, frame = video.read()
    if not ret:
        return
    height, width, _ = frame.shape

    frameSize = (height, width)
    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    output = cv.VideoWriter(out_path, fourcc=fourcc,
                            fps=fps, frameSize=frameSize)

    M = cv.getRotationMatrix2D((width/2, height/2), rotate_angle, scale)

    while ret:
        frame = np.rot90(frame, -1)
        output.write(frame)
        ret, frame = video.read()

    video.release()
    output.release()
    cv.destroyAllWindows()


def overlap_bbox_on_video(video_path, bbox_path, bbox_flag_path, search_area_path, out_path=None, thickness=5, fps=30.0, extra='', debug=False):
    if out_path in [None, '']:
        video_path_split = video_path.split('.')
        video_path_split[-2] += "+BBox"
        if not search_area_path in [None, '']:
            video_path_split[-2] += "+Search_Area"
        video_path_split[-2] += extra
        out_path = '.'.join(video_path_split)
        out_path = out_path.replace('mp4', 'avi')

    bbox_file = open(bbox_path)
    bbox_lines = bbox_file.readlines()

    bbox_flag_file = open(bbox_flag_path)
    bbox_flag_lines = bbox_flag_file.readlines()

    if not search_area_path in [None, '']:
        search_area_file = open(search_area_path)

    video = cv.VideoCapture(video_path)
    ret, frame = video.read()
    if not ret:
        return

    height, width, _ = frame.shape
    frameSize = (width, height)
    fourcc = cv.VideoWriter_fourcc(*'MJPG')
    output = cv.VideoWriter(out_path, fourcc=fourcc,
                            fps=fps, frameSize=frameSize)

    for i, line in enumerate(bbox_lines):
        if i != 0:
            ret, frame = video.read()

        frame_copy = frame.copy()

        if search_area_path != None:
            search_area_line = search_area_file.readline()
            if search_area_line != '':
                l, b, w, h = tuple(map(int, search_area_line.split()))
                left_corner, right_corner = (l, b), (l+w, b+h)
                cv.rectangle(frame_copy, left_corner, right_corner,
                             color=_bbox_colors['search'], thickness=thickness)

        l, b, w, h = tuple(map(int, line.split()))
        left_corner, right_corner = (l, b), (l+w, b+h)

        cv.rectangle(frame_copy, left_corner, right_corner,
                     color=_bbox_colors[bbox_flag_lines[i][:-1]], thickness=thickness)
        output.write(frame_copy)

    bbox_file.close()
    bbox_flag_file.close()
    if not search_area_path in [None, '']:
        search_area_file.close()
    video.release()
    output.release()
    cv.destroyAllWindows()

    return out_path


def merge_videos(in_paths, out_path, fps=30.0, mode='horizontal'):
    import numpy as np

    videos = []
    for path in in_paths:
        video = cv.VideoCapture(path)
        videos.append(video)

    num = len(videos)

    out_video = None
    fourcc = cv.VideoWriter_fourcc(*'MJPG')

    ret = True
    while ret:
        frames = []
        for video in videos:
            ret, frame = video.read()
            if not ret:
                break
            frames.append(frame)
            if out_video == None:
                height, width, _ = frame.shape
                if mode == 'horizontal':
                    width *= num
                else:
                    height *= num
                frameSize = (width, height)
                out_video = cv.VideoWriter(
                    out_path, fourcc=fourcc, fps=fps, frameSize=frameSize)
        if ret:
            frames = np.hstack(
                frames) if mode == 'horizontal' else np.vstack(frames)
            out_video.write(frames)

    for video in videos:
        video.release()
    cv.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description='Run converter to create new video.')
    parser.add_argument('mode', type=str,
                        help='Name of the video generation method.')
    parser.add_argument('--debug', type=bool, default=False)
    parser.add_argument('--input_video', type=str,
                        default='', help='Path of the input video to be modified.')
    parser.add_argument('--input_bbox', type=str,
                        default='', help='Path of the bounding box of the input video.')
    parser.add_argument('--input_flag', type=str, default='',
                        help='Path of the flag of the bounding box.')
    parser.add_argument('--input_search', type=str, default='',
                        help='Path of the search area of the input video.')
    parser.add_argument('--output_video', type=str,
                        default='', help='Path of the output video.')
    parser.add_argument('--rotate', type=bool, default=False,
                        help='If rotate the output video.')
    parser.add_argument('--angle', type=float, default=-90.0,
                        help='The rotating angle of the input video.')
    parser.add_argument('--tracker_name', type=str,
                        default='dimp', help='Name of tracking method.')
    parser.add_argument('--tracker_param', type=str,
                        default='dimp50', help='Name of parameter file.')

    args = parser.parse_args()

    if args.mode == 'image2video':
        tracking_results_path = "/home/sifan/Documents/Zhang/pytracking/pytracking/tracking_results"
        tracking_results_path += "/" + args.tracker_name
        tracking_results_path += "/" + args.tracker_param

        file_list = os.listdir(tracking_results_path)
        file_list.sort()

        for i, filename in enumerate(file_list):
            if os.path.isfile(os.path.join(tracking_results_path, filename)):
                del file_list[i]

        path_list = list(map(lambda x: os.path.join(
            tracking_results_path, x), file_list))

        for file, path in zip(file_list, path_list):
            convert_images_to_video(
                path, path+'/'+file+'.avi', fps=30.0, frameSize=None, image_type='jpg')
    elif args.mode == 'bbox':
        print("Creating video from bounding boxes.")
        search_area_scale = input("What is the search area scale: ")
        sample_memory_size = input("What is the sample memory size: ")
        extra = input("Extra information: ")
        if extra != '':
            extra = '+' + extra
        extra = '+Sample_Memory_size={}+Search_Area_Scale={}'.format(
            sample_memory_size, search_area_scale) + extra
        out_path = overlap_bbox_on_video(args.input_video, args.input_bbox, args.input_flag, args.input_search,
                                         thickness=8, extra=extra)
        if args.rotate:
            rotate_video(out_path, args.angle)
    elif args.mode == 'merge':
        print("Merging videos.")
        in_paths = []
        in_paths.append(
            "/home/sifan/Documents/pytracking/pytracking/datasets/Videos/Office/[P]Office_001_960x540+Search_Area+BBox+Sample_Memory_size=30+Search_Area_Scale=5.avi")
        in_paths.append(
            "/home/sifan/Documents/pytracking/pytracking/datasets/Videos/Office/[F]Office_001_960x540+Search_Area+BBox+Sample_Memory_size=30.avi")

        out_path = "/home/sifan/Videos/[PF]Office_001_960x540+Results+Vertical.avi"
        merge_videos(in_paths, out_path, mode='vertical')


if __name__ == '__main__':
    main()
