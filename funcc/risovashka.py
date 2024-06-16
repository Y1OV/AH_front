import pandas as pd
import streamlit as st
import cv2
import numpy as np
import requests
import json
import zipfile
from PIL import Image, UnidentifiedImageError
import io
import os


def draw_bounding_box(image, box, class_id, class_names, colors, box_thickness=3, font_scale=0.8, font_thickness=2):
    height, width, _ = image.shape
    x_center, y_center, w, h = box

    xmin = int((x_center - w / 2) * width)
    xmax = int((x_center + w / 2) * width)
    ymin = int((y_center - h / 2) * height)
    ymax = int((y_center + h / 2) * height)

    color = colors[class_id]

    cv2.rectangle(image, (xmin, ymin), (xmax, ymax), color, box_thickness)

    label = f"{class_names[class_id]}"
    (label_width, label_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness)

    cv2.rectangle(image, (xmin, ymin - label_height - baseline), (xmin + label_width, ymin), color, cv2.FILLED)
    cv2.putText(image, label, (xmin, ymin - baseline), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), font_thickness)


def visualize_annotations(image, annotations, class_names, colors, box_thickness=3, font_scale=0.8, font_thickness=2):
    image = np.array(image)
    unique_class_ids = set()
    for annotation in annotations:
        class_id = int(annotation['class_id'])
        unique_class_ids.add(class_id)
        box = (annotation['rel_x'], annotation['rel_y'], annotation['width'], annotation['height'])
        draw_bounding_box(image, box, class_id, class_names, colors, box_thickness, font_scale, font_thickness)

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    unique_classes = [class_names[id] for id in unique_class_ids]
    return image, unique_classes
