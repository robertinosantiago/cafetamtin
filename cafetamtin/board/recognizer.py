# Copyright (C) 2022 Robertino Mendes Santiago Junior
# 
# This file is part of CaFE-TaMTIn Approach.
# 
# CaFE-TaMTIn Approach is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CaFE-TaMTIn Approach is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with CaFE-TaMTIn Approach.  If not, see <http://www.gnu.org/licenses/>.

from asyncore import read
import cv2
import numpy as np
import imutils

class Recognizer:

    def __init__(self, board):
        self.yolo_labels = '../data/yolov4-tiny/obj.names'
        self.yolo_weight = '../data/yolov4-tiny/training/yolov4-tiny-custom_best.weights'
        self.yolo_config = '../data/yolov4-tiny/yolov4-tiny-custom.cfg'
        self.net = cv2.dnn.readNet(self.yolo_weight, self.yolo_config)
        self.board = board
        self.classes = []
        self.colors = []

        self.load_classes()
        self.load_colors()

    def load_classes(self):
        with open(self.yolo_labels, 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

    def load_colors(self):
        self.colors = np.random.uniform(0, 255, size=(len(self.classes), 3))
    
    #separar
    def take_picture(self):
        return self.board.camera.take_picture()
    
    def get_output_layers(self):
        layer_names = self.net.getLayerNames()
        output_layers = [layer_names[i - 1] for i in self.net.getUnconnectedOutLayers()]
        return output_layers

    def draw_prediction(self, img, class_id, confidence, x, y, x_plus_w, y_plus_h):
        label = str(self.classes[class_id])
        self.load_colors()
        color = self.colors[class_id]
        cv2.rectangle(img, (x,y), (x_plus_w,y_plus_h), color, 2)
        cv2.putText(img, label, (x-10,y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    def get_positions(self, image, draw_box = False):
        positions = {}

        #height, width, channels = image.shape
        height, width = image.shape
        blob = cv2.dnn.blobFromImage(image, 1/255, (width, height),(0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.get_output_layers())

        class_ids = []
        confidences = []
        boxes = []
        centers = []
        conf_threshold = 0.5
        nms_threshold = 0.4

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    # Extract values to draw bounding box
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    centers.append([center_x, center_y])
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

                    print('center: x:{}, y:{} = Number: {}'.format(center_x, center_y, self.classes[class_id]))
                    self.draw_prediction(image, class_id, confidence, round(x), round(y), round(x+w), round(y+h))
                    cv2.imwrite("object-detection.jpg", image)

        print(boxes)
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        print('indices: ', indices)
        print('boxes:', boxes)
        print('centers:', centers)

        for i in indices:
            #i = i[0]
            #print(i)
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            positions[self.classes[class_ids[i]]] = {
                'confidence': confidences[i],
                'x': round(x),
                'y': round(y),
                'w': round(w),
                'h': round(h),
                'center_x': round(centers[i][0]),
                'center_y': round(centers[i][1])
            }

            if draw_box:
                if (self.classes[class_ids[i]] != 'board'):
                    self.draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x+w), round(y+h))
                    cv2.imwrite("object-detection.jpg", image)

        return positions