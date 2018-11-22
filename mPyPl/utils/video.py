import numpy as np
import cv2
from os.path import *
import math

# trs, let's assume width is always wider than height
def video_to_npy(infile, outfile=None, width=None,  height=None, squarecrop=None, fps=None, mode='rgb', maxlength=None, use_cache=False):

    global vcache

    if use_cache and outfile is not None and 'vcache' in globals():
        if outfile in vcache: return vcache[outfile]
    else:
        vcache = dict()

    # has this video already been saved before?
    if outfile and isfile(outfile):
        frames = np.load(outfile)

        if use_cache: vcache[outfile] = frames
        # just return this preloaded video
        return frames
    
    print('reading fresh video from %s' % infile)
    vidcap = cv2.VideoCapture(infile)
    success, image = vidcap.read()
    
    frames = []
    count = 0
    if not success:
        raise ValueError('Could not read the video file!')
    while success:
        frames.append( image[...,::-1] if mode == 'rgb' else image )
        count += 1
        success,image = vidcap.read()
    if fps:
        span = int(vidcap.get(cv2.CAP_PROP_FPS) / fps)
        frames = frames[0::span] 
    if width or height:  
        width = width if width else int(height / frames[0].shape[0] * frames[0].shape[1])
        height = height if height else int(width / frames[0].shape[1] * frames[0].shape[0])
        frames = [ cv2.resize(frame, (width, height)) for frame in frames ]
    if squarecrop:
        tl = int((width/2)-(height/2))
        # note that x,y is the wrong way around i.e. it's
        # F x Y x X x C
        frames = [ frame[ 0:height, tl:(tl+height)] for frame in frames ]
    # trs-renamed this from "cropat" as it's a more intuative name
    if maxlength:
        frames = frames[0:maxlength*fps]
        
    frames = np.array(frames)
    if outfile:
        np.save(outfile, frames)
    return frames

def resize_video(video, video_size=(100,100)):
    """
    Resize video content
    """
    width, height = video_size
    width = width if width else int(height / video[0].shape[0] * video[0].shape[1])
    height = height if height else int(width / video[0].shape[1] * video[0].shape[0])
    video = np.array([ cv2.resize(frame, (width, height)) for frame in video ])
    return video

def dense_optical_flow(frame1, frame2):
    f1 = cv2.cvtColor(frame1,cv2.COLOR_BGR2GRAY)
    f2 = cv2.cvtColor(frame2,cv2.COLOR_BGR2GRAY)
    return cv2.calcOpticalFlowFarneback(f1, f2, None, 0.5, 3, 15, 3, 5, 1.2, 0)

def flow_to_hsv(frame1, flow):
    hsvImg = np.zeros_like(frame1)
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsvImg[..., 0] = 0.5 * ang * 180 / np.pi
    hsvImg[..., 1] = 255
    hsvImg[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    return cv2.cvtColor(hsvImg, cv2.COLOR_HSV2BGR)

def naive_stabilization(f):
    vec = np.average(f,axis=(0,1))
    mask = f==0
    f = f-vec
    f[mask]=0
    return f

def flow_to_polar(f):
    return cv2.cartToPolar(f[..., 0], f[..., 1])
