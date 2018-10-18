# Video processing functions
from .utils.video import *
from pipe import Pipe

def videosource_chunked(fname,frames_per_chunk=25,video_size=(100,100),mode='rgb'):
    vidcap = cv2.VideoCapture(fname)
    success, image = vidcap.read()
    i = 0
    # TODO: We assume that video is color
    chunk = np.zeros((frames_per_chunk,video_size[1],video_size[0],3))
    if not success:
        raise ValueError('Could not read the video file!')
    while success:
        im=resize_frame((image[..., ::-1] if mode == 'rgb' else image),video_size)
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
def collect_video(datastream,filename,video_size=None):
    w = None
    for x in datastream:
        if w is None:
            if video_size is None:
                video_size = x.shape[-2:-4:-1]
            w = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*"ffds"), 25, video_size)
        #TODO: need resize in case video_size is not the same as data shape
        if len(x.shape)<=3:
            w.write(np.uint8(x))
        else:
            for z in x:
                w.write(np.uint8(z))