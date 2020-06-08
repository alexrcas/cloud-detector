import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import zmq
import base64
import numpy as np
import json
import requests
import io
import matplotlib as plt

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

from flask import Flask, request, Response

app = Flask(__name__)




MODEL_NAME = 'ssd_mobilenet_v1_0.75_depth_300x300_coco14_sync_2018_07_03'
MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'

PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.compat.v1.GraphDef()
    with tf.io.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')


label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(
    label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape(
        (im_height, im_width, 3)).astype(np.uint8)


class Object(object):
    def __init__(self):
        self.name="webrtcHacks TensorFlow Object Detection REST API"

    def toJSON(self):
        return json.dumps(self.__dict__)


def get_objects(image, sessionID, threshold=0.5):
    with detection_graph.as_default():
        with tf.compat.v1.Session(graph=detection_graph) as sess:
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
          
            image_np = load_image_into_numpy_array(image)
            image_np_expanded = np.expand_dims(image_np, axis=0)
            (boxes, scores, classes, num) = sess.run(
                [detection_boxes, detection_scores, detection_classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            classes = np.squeeze(classes).astype(np.int32)
            scores = np.squeeze(scores)
            boxes = np.squeeze(boxes)

            obj_above_thresh = sum(n > threshold for n in scores)

            output = []
            item = Object()
            item.version = "0.0.1"
            item.numObjects = float(obj_above_thresh)
            item.threshold = threshold
            output.append(item)


            for c in range(0, len(classes)):
                class_name = category_index[classes[c]]['name']
                if scores[c] >= threshold:
                    if class_name == 'person' and scores[c] > 0.5:
                        files = {'image': image_np.tostring(), 'sessionID': sessionID}
                        response = requests.post('http://localhost:5000/detection', files = files)


                    item = Object()
                    item.name = 'Object'
                    item.class_name = class_name
                    item.score = float(scores[c])
                    item.y = float(boxes[c][0])
                    item.x = float(boxes[c][1])
                    item.height = float(boxes[c][2])
                    item.width = float(boxes[c][3])
                    output.append(item)

            outputJson = json.dumps([ob.__dict__ for ob in output])
            return outputJson



@app.route('/image', methods=['POST'])
def image():
    try:
        sessionID = request.files['sessionID'].read().decode('utf-8')
        image_file = request.files['image']
        image_object = Image.open(image_file)
        objects = get_objects(image_object, sessionID)
        return objects
    except Exception as e:
        return e



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
