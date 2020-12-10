from face_rhythm.util import helpers
import cv2
import numpy as np
import skimage.draw


RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)
WHITE = (255, 255, 255)
colors = (WHITE , RED, GREEN, BLUE, CYAN, MAGENTA, YELLOW)
pts = []



def load_video(vidToSet, frameToSet, path_vid_allFiles):
    path_vid = path_vid_allFiles[vidToSet-1]
    video = cv2.VideoCapture(path_vid)
    
    video.set(1,frameToSet)
    ok, frame = video.read()
    return frame
# cv2.waitKey(1);


## The below block is adapted code. It makes a GUI, then allows a user to click to define the
## outline of the ROI to use. 'pts' are the clicked points.
 # prepare for appending. I'm using this global in functions like a pleb. please forgive
def draw(x):
    d = cv2.getTrackbarPos('thickness', 'window')
    d = 1 if d==0 else d
    i = cv2.getTrackbarPos('color', 'window')
    color = colors[i]
    cv2.polylines(frame, np.array([pts]), False, color, d)
    cv2.imshow('window', frame)
    text = f'color={color}, thickness={d}'
#     cv2.displayOverlay('window', text)


def mouse(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        pts.append((x, y))
        draw(0)

        
def create_seg(frame):
    cv2.imshow('window', frame)
    cv2.setMouseCallback('window', mouse)
    cv2.createTrackbar('color', 'window', 0, 6, draw)
    cv2.createTrackbar('thickness', 'window', 1, 10, draw)
    draw(0)
    cv2.waitKey(0)
    ## The below block "fills in" the indices of all the points within the above defined bounds
    mask_frame = np.zeros((frame.shape[0] , frame.shape[1]))
    pts_y, pts_x = skimage.draw.polygon(np.array(pts)[:,1], np.array(pts)[:,0])
    mask_frame[pts_y, pts_x] = 1

    cv2.imshow('window', frame * np.uint8(np.repeat(mask_frame[:,:,None] , 3 , axis=2)))

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    return pts_y, pts_x, mask_frame


def get_bbox(mask_frame):
    bbox = np.zeros(4)
    bbox[0] = np.min(np.where(np.max(mask_frame , axis=0))) # x top left
    bbox[1] = np.min(np.where(np.max(mask_frame , axis=1))) # y top left
    bbox[2] = np.max(np.where(np.max(mask_frame , axis=0))) - bbox[0] # x size
    bbox[3] = np.max(np.where(np.max(mask_frame , axis=1))) - bbox[1] # y size
    bbox = np.int64(bbox)
    return bbox


def roi_workflow(config_filepath):
    config = helpers.load_config(config_filepath)
    global frame
    frame = load_video(config['vidToSet'],config['frameToSet'],config['path_vid_allFiles'])
    pts_y, pts_x, mask_frame = create_seg(frame)
    bbox = get_bbox(mask_frame)
    bbox_subframe_displacement = bbox
    pts_displacement , pts_x_displacement , pts_y_displacement = pts , pts_x , pts_y
    mask_frame_displacement = mask_frame
    cv2.destroyAllWindows()
    pts_all = dict([
    ('bbox_subframe_displacement', bbox_subframe_displacement), 
    ('pts_displacement', pts_displacement), 
    ('pts_x_displacement', pts_x_displacement),
    ('pts_y_displacement', pts_y_displacement),
    ('mask_frame_displacement', mask_frame_displacement)
    ])
    return pts_all