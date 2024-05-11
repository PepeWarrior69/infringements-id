import numpy as np
import cv2
import os
import uuid
import requests
import asyncio
from time import time
from PIL import Image

DISPLAY_IMAGES = os.environ.get('DISPLAY_IMAGES', 'true') == 'true'

lower_red_hsv_1 = np.array([ 0, 175, 20 ])
higher_red_hsv_1 = np.array([ 10, 255, 255 ])
# lower_red_hsv_2 = np.array([ 170, 175, 20 ])
# higher_red_hsv_2 = np.array([ 180, 255, 255 ])

lower_red_hsv_2 = np.array([ 175, 175, 100 ])
higher_red_hsv_2 = np.array([ 180, 255, 255 ])

haar_cascade = os.environ.get('HAAR_CASCADE_PATH', 'C:\studyProjects\infringements-id\src\cars.xml')
CLF = cv2.CascadeClassifier(haar_cascade)
FONT = cv2.FONT_HERSHEY_COMPLEX

# Configuration
offset = 6
min_width = 80
min_height = 80

ground_truth1 = 62
ground_truth2 = 36

# Colors and Constants
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (176, 130, 39)
ORANGE = (0, 127, 255)

def center_position(x, y, w, h):
    center_x = x + (w // 2)
    center_y = y + (h // 2)
    return center_x, center_y

detect_vehicle = []

# https://medium.com/@gowtham180502/how-to-detect-colors-using-opencv-python-98aa0241e713
class IncidentAnalyzer:
    def __init__(self):
        self.vehicle_counts = 0
        self.frames_since_last_save = 0
    
    def is_red_traffic_light(self, traffic_frame):
        # return np.any(mask > 0)
        
        hsv_frame = cv2.cvtColor(traffic_frame, cv2.COLOR_BGR2HSV)
        
        # mask_1 = cv2.inRange(hsv_frame, lower_red_hsv_1, higher_red_hsv_1)
        mask_2 = cv2.inRange(hsv_frame, lower_red_hsv_2, higher_red_hsv_2)
        
        # mask = mask_1 + mask_2
        
        detected_frame = cv2.bitwise_and(traffic_frame, traffic_frame, mask=mask_2)
        if DISPLAY_IMAGES:
            cv2.imshow('traffic_frame', detected_frame)
        
        return np.any(mask_2 > 0)
    
    def check_frame_for_car(self, name, frame):
        is_car_detected = False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 5)

        # Pass frame to our car classifier
        vehicle = CLF.detectMultiScale(
            blur,
            scaleFactor=1.2,    # how much the image size is reduced at each image scale
            minNeighbors=2,     # how many neighbors each candidate rectangle should have to retain it
            minSize=(min_width, min_height)
        )

        # Extract bounding boxes for any car identified
        for (x, y, w, h) in vehicle:
            cv2.rectangle(frame, (x, y), (x + w, y + h), GREEN, 2)

            center = center_position(x, y, w, h)
            detect_vehicle.append(center)
            cv2.circle(frame, center, 4, RED, -1)
            self.vehicle_counts += 1
            is_car_detected = True
    
        if DISPLAY_IMAGES:
            cv2.imshow(f'Vehicles Detection on {name}', frame)
        
        return is_car_detected, frame
    
    async def register_incident(self, epoch, road_frame_filename, full_frame_filename):
        endpoint = os.environ.get('API_ENDPOINT', None)
        payload = {
            'is_red_traffic_light_detected': True,
            'epoch': epoch,
            'road_frame_filename': road_frame_filename,
            'full_frame_filename': full_frame_filename,
        }
        
        if not endpoint:
            print('Endpoint is missing!')
        
        try:
            await requests.post(endpoint, json=payload)
        except Exception as err:
            print(f'Error during POST request ({endpoint=}) err = ', err)
    
    def analyze_frame(self, frame):
        tl_x, tl_y, tl_width, tl_height = 1615, 365, 25, 22
        
        image = Image.fromarray(frame).convert('RGB')

        
        traffic_light_rect = image.crop((tl_x, tl_y, tl_x + tl_width, tl_y + tl_height))
        # size = 300, 300
        # resized = traffic_light_rect.resize(size)
        traffic_frame = np.array(traffic_light_rect)
        
        if DISPLAY_IMAGES:
            cv2.imshow('Original Frame', frame)
        
        is_traffic_light_red = self.is_red_traffic_light(traffic_frame)
        
        if not is_traffic_light_red:
            return
        
        # cutting only specific part of a road
        road_x, road_y, road_width, road_height = 700, 800, 1220, 280
        road_rect = image.crop((road_x, road_y, road_x + road_width, road_y + road_height))
        road_frame = np.array(road_rect)
        
        is_detected, analyzed_road_frame = self.check_frame_for_car('road frame', road_frame)
        
        if is_detected and self.frames_since_last_save > 10:
            _, analyzed_road_full_frame = self.check_frame_for_car('full frame', frame)
            storage = os.environ.get('STORAGE_PATH', 'C:\studyProjects\infringements-id\storage')
            
            print('storage PATH = ', storage)
            
            os.chdir(storage)
            
            # save images
            epoch = round(time() * 1000)
            unique_id = f'{epoch}_{uuid.uuid4().hex}'
            road_frame_filename = f'{unique_id}_analyzed_road_frame.webp'
            full_frame_filename = f'{unique_id}_analyzed_road_full_frame.webp'
            
            try:
                img1 = Image.fromarray(analyzed_road_frame).convert('RGB')
                img1.save(road_frame_filename, 'webp', optimize = True, quality = 10)
                img2 = Image.fromarray(analyzed_road_full_frame).convert('RGB')
                img2.save(full_frame_filename, 'webp', optimize = True, quality = 10)
            except Exception as err:
                print(f'Error during file save: err = ', err)
                
            self.frames_since_last_save = 0
            
            # call API to add new incident
            self.register_incident(epoch, road_frame_filename, full_frame_filename)
        else:
            self.frames_since_last_save += 1
            
        