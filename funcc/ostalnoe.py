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

def get_recommendations(unique_classes):
    recommendations_dict = {
        'adj': "Используйте правильные параметры сварки. Поддерживайте чистоту сварочной поверхности. Проверьте качество сварочных материалов. Применяйте антипригарные спреи или пасты. Следите за стабильностью дуги и избегайте слишком длинной дуги.",
        'int': "Завершайте сварку с заполнением кратера. Очистите поверхность от шлака после каждого прохода. Улучшите подготовку краев. Избегайте влажности в сварочных материалах. Уменьшите ток или скорость подачи проволоки. Поддерживайте чистоту сварочных материалов.",
        'geo': "Уменьшите ток или скорость сварки. Улучшите подготовку краев. Увеличьте скорость сварки или уменьшите подачу материала. Проверьте параметры сварки для оптимального расплавления. Следите за балансом тепла и подачи материала. Проверьте настройки сварочного оборудования.",
        'pro': "Применяйте правильные методы резки и шлифовки. Используйте подходящие инструменты для удаления заусенцев. Следите за аккуратностью резки и формовки. Убедитесь в правильном использовании инструментов и их остроте. Следите за осторожным обращением с материалами и готовыми изделиями.",
        'non': "Улучшите подготовку краев и стыковку элементов. Применяйте методы заполнения и оптимальные параметры сварки. Используйте более качественные сварочные материалы. Проверьте настройки сварочного оборудования и параметры сварки. Убедитесь, что подготовка краев и очистка поверхности выполнены правильно."
    }
    recommendations = {}
    for cls in unique_classes:
        if cls in recommendations_dict:
            recommendations[cls] = recommendations_dict[cls]
    return recommendations

def process_zip_file(zip_file, class_names, colors):
    results = []
    with zipfile.ZipFile(zip_file, 'r') as archive:
        for idx, file_info in enumerate(archive.infolist()):
            file_name = file_info.filename
            if file_name.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    # Очистка имени файла
                    safe_name = os.path.basename(file_name)
                    safe_name = safe_name.replace("(", "").replace(")", "").replace(" ", "_")

                    with archive.open(file_info) as file:
                        image = Image.open(file)
                        image = image.convert("RGB")  # Конвертация изображения в RGB
                        img_array = np.array(image)
                        _, img_encoded = cv2.imencode('.jpg', img_array)
                        img_bytes = img_encoded.tobytes()

                        addr = 'https://6152-83-143-66-61.ngrok-free.app'
                        test_url = addr + '/api/test'
                        content_type = 'image/jpeg'
                        headers = {'content-type': content_type}

                        response = requests.post(test_url, data=img_bytes, headers=headers)

                        if response.status_code == 200:
                            annotations = json.loads(response.text)
                            annotated_image, unique_classes = visualize_annotations(image, annotations, class_names, colors)
                            results.append((f"{idx}_{safe_name}", annotated_image, unique_classes))
                        else:
                            st.error(f"Ошибка при получении аннотаций для файла {safe_name}.")
                except UnidentifiedImageError:
                    pass
                except Exception as e:
                    pass
    return results
