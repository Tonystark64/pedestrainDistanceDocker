import math
import json
import cv2
import ast
import time 
import os 
import configparser
from flask import Flask, Response

# find root path of application
app = Flask(__name__)

# change dir to the folder where current script exists
current_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(current_dir)

# Load the configuration file
config = configparser.ConfigParser()
config.read('config.ini')
json_path = config.get('settings', "json_path")
video_path = config.get('settings', 'video_path')
real_x = config.getint('settings', 'real_x')
real_y = config.getint('settings', 'real_y')
jsonStart = config.getint('settings','jsonStart')
scale = config.getfloat('settings','scale')
max_distance = config.getfloat('settings','max_distance')
distThreshold = config.getfloat('settings','distThreshold')

def distance(p1, p2):
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)

def calculate_distances(json_data, real_x, real_y, scale, max_distance):
    distances = []
    for frame in json_data:  
        frame_distances = {}  
        persons = [obj for obj in frame['objects'] if obj['name'] == 'person']
        for i, obj1 in enumerate(persons): # every two persons
            for j, obj2 in enumerate(persons[i + 1:]):
                # frame width and frame height
                center1 = obj1['relative_coordinates']['center_x'] * real_x, obj1['relative_coordinates'][
                    'center_y'] * real_y
                center2 = obj2['relative_coordinates']['center_x'] * real_x, obj2['relative_coordinates'][
                    'center_y'] * real_y
                d = distance(center1, center2) * scale  
                if d <= max_distance:
                    # save distance between obj1 and obj2
                    pos1 = "(" + str(obj1['relative_coordinates']['center_x']) + ", " + \
                           str(obj1['relative_coordinates']['center_y']) + ")"
                    pos2 = "(" + str(obj2['relative_coordinates']['center_x']) + ", " + \
                           str(obj2['relative_coordinates']['center_y']) + ")"
                    frame_distances.update({pos1 + " | " + pos2: d})
        distances.append(frame_distances)
    return distances


def displayVideo():

    with open(json_path) as f:
        jdata = json.load(f)
    # we get the distance information from json file output from opendatacam
    result = calculate_distances(jdata, real_x, real_y, scale, max_distance)


    # read in the video
    cap = cv2.VideoCapture(video_path)

    # loop through each frame of the video
    frameN = 0
    mid = 0
    while cap.isOpened():
        ret, frame = cap.read()
        frameN = frameN + 1
        if not ret:
            break

        map_list = {}  # replace with your map list for this frame
        if frameN > jsonStart:
            map_list = result[int(mid)]
            mid = mid + 1
            # time lag between frames to show lines and distances clearly
            time.sleep(0.2)

        # loop through each key-value pair in the map list
        for key, value in map_list.items():
            # extract the x,y positions of the two persons
            pos1, pos2 = key.split(' | ')
            x1, y1 = ast.literal_eval(pos1)
            x2, y2 = ast.literal_eval(pos2)
            # draw the distance line
            pt1 = (int(x1 * frame.shape[1]), int(y1 * frame.shape[0]))
            pt2 = (int(x2 * frame.shape[1]), int(y2 * frame.shape[0]))
            color = (0, 255, 0)
            thickness = 2
            if value < distThreshold:
                # draw lines and distances
                cv2.line(frame, pt1, pt2, color, thickness)
                cv2.putText(frame,str(value)[:6],(int((pt1[0]+pt2[0])/2), int((pt1[1]+pt2[1])/2)),\
                            cv2.FONT_HERSHEY_COMPLEX,0.5,(102,255,255),1)

        # display the frame in python IDE
        # cv2.imshow('frame', frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
            # break
        
        # display in the web browser
        ret, buffer = cv2.imencode('.jpg', frame)
        # yield the image as byte string
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    # Set the response headers to indicate that this is a multipart response
    return Response(displayVideo(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    # specify host and port
    # better to use different port map
    app.run(host="0.0.0.0",port=5000,debug=True)