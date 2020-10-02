# Video processing functions
from .utils.video import *
from .utils.image import im_resize
from pipe import Pipe
from PIL import Image
from PIL import GifImagePlugin


def load_video(video, video_size=(100,100), squarecrop=False, fps=25, maxlength=5, use_cache=False):
    """
    Load video content into `np.array.`. This is most frequently used to load video files for further processing in a
    pipeline like this:
    `get_datastream(...) | apply('filename','video',load_video) | ...`
    """
    return video_to_npy(
        video,
        width=video_size[0],
        height=video_size[1],
        squarecrop=squarecrop,
        fps=fps,
        maxlength=maxlength,
        use_cache=use_cache
    )

def videosource(fname,video_size=(100,100),mode='rgb'):
    """
    Produce a stream of video frames from a given input file.
    :param fname: input file name (video)
    :param video_size: tuple showing the size of the video frames `(width,height)`
    :param mode: mode used to open the file. Default is `'rgb'`
    :return: pipe stream of video frames
    """
    vidcap = cv2.VideoCapture(fname)
    success, image = vidcap.read()
    # TODO: We assume that video is color
    if not success:
        raise ValueError('Could not read the video file!')
    while success:
        im=im_resize((image[..., ::-1] if mode == 'rgb' else image),video_size)
        yield im
        success, image = vidcap.read()


def videosource_chunked(fname,frames_per_chunk=25,video_size=(100,100),mode='rgb'):
    """
    Produce a stream of video chunks of a given size.
    :param fname: input filename
    :param frames_per_chunk: number of frames per chunk. Defaults to 25, meaning 1 second of video under 25 fps.
    :param video_size: tuple showing the size of the video frames `(width,height)`
    :param mode: mode used to open the file. Default is `'rgb'`
    :return: pipe stream of video chunks
    """
    vidcap = cv2.VideoCapture(fname)
    success, image = vidcap.read()
    i = 0
    # TODO: We assume that video is color
    chunk = np.zeros((frames_per_chunk,video_size[1],video_size[0],3))
    if not success:
        raise ValueError('Could not read the video file!')
    while success:
        im=im_resize((image[..., ::-1] if mode == 'rgb' else image),video_size)
        chunk[i] = im
        i+=1
        if i==frames_per_chunk:
            yield chunk
            i=0
            chunk = np.zeros((frames_per_chunk, video_size[1], video_size[0], 3)) # TODO: Color!
        success, image = vidcap.read()        

@Pipe
def chunk_slide(datastream, chunk_size):
    # preload into memory
    # TODO: this will throw exception if windows size is smaller than first chunk
    mem = np.array([next(datastream) for _ in range(chunk_size)])
    for x in datastream:
        yield mem.reshape((-1,)+x.shape[-3:]).copy()
        mem = np.roll(mem, -1, axis=0)
        mem[-1] = x

@Pipe
def collect_video(datastream,filename,video_size=None,codec=cv2.VideoWriter_fourcc(*"ffds")):
    """
    Collect a video file from a sequence of frames of video fragments.
    :param datastream: sequence of images or video fragments
    :param filename: output file name
    :param video_size: size of the video. If `None` (which is the default) - video size is determined from the dimensions of the input `np.array`
    :param codec: OpenCV codec to use. Default is `cv2.VideoWriter_fourcc(*"ffds")`
    """
    w = None
    for x in datastream:
        if w is None:
            if video_size is None:
                video_size = x.shape[-2:-4:-1]
            w = cv2.VideoWriter(filename, codec, 25, video_size)
        #TODO: need resize in case video_size is not the same as data shape
        if len(x.shape)<=3:
            w.write(np.uint8(x))
        else:
            for z in x:
                w.write(np.uint8(z))