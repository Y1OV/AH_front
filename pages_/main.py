import pandas as pd
import streamlit as st
import cv2
import numpy as np
import requests
import json
from PIL import Image

# HTML-код для логотипа
html_code = '''
<div style="text-align: center;">
    <a href="https://raw.githubusercontent.com/Y1OV/DFO_front/main/lct/rosatom-logo-brandlogos.net.png">
        <img src="https://raw.githubusercontent.com/Y1OV/DFO_front/main/lct/rosatom-logo-brandlogos.net.png" alt="Foo" style="width: 50%; height: auto;">
    </a>
</div>
'''

# Функция для отрисовки рамок вокруг дефектов
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

# Функция для визуализации аннотаций
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

# Функция для получения рекомендаций по дефектам
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

# Основная функция Streamlit приложения
def main():
    st.title("Определение дефектов сварных швов")

    st.markdown(html_code, unsafe_allow_html=True)

    st.text_area(
        "⚙️ Как это работает?",
        "Модель на основе ИИ анализирует полученное изображение, "
        "используя YoLOv10 и RTDETR для распознавания и детекции,"
        "и возвращает картинку с размеченными дефектами.",
        height=100
    )

    tab1, tab2 = st.tabs(["YoLOv10😎📊", "RTDETR🚀💻"])

    with tab1:
        st.title("Загрузка и отображение изображения")

        uploaded_image = st.file_uploader("Выберите изображение...", type=["jpg", "jpeg", "png"],key="uploader1")

        class_names = ['adj', 'int', 'geo', 'pro', 'non']
        colors = {
            0: (255, 0, 255),
            1: (255, 0, 0),
            2: (0, 255, 0),    
            3: (0, 0, 255),  
            4: (255, 255, 0)
        }
    

        if st.button("Распознать дефекты", key="single_button_1"):

            if uploaded_image is not None:
                image = Image.open(uploaded_image)
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

                    st.image(annotated_image, caption='Изображение с аннотациями', use_column_width=True)

                    if unique_classes:
                        unique_classes_str = ', '.join(unique_classes)
                        st.text(f"Дефекты на изображении: {unique_classes_str}")

                        st.markdown(
                            f"<span style='color:yellow'>{'Рекомендации:'}</span>",
                            unsafe_allow_html=True
                        )
                        recommendations = get_recommendations(unique_classes)
                        
                        for cls, rec in recommendations.items():
                            st.text_area(f"Рекомендации для {cls}", rec, height=100)
                    else:
                        st.text("Дефекты отсутствуют")
                else:
                    st.error("Ошибка при получении аннотаций от API.")
            else:
                st.error("Пожалуйста, загрузите изображение.")

    with tab2:
        st.title("Загрузка и отображение изображения")

        uploaded_image = st.file_uploader("Выберите изображение...", type=["jpg", "jpeg", "png"], key="uploader2")

        class_names = ['adj', 'int', 'geo', 'pro', 'non']
        colors = {
            0: (255, 0, 0),    # adj - красный
            1: (0, 255, 0),    # int - зеленый
            2: (0, 0, 255),    # geo - синий
            3: (255, 255, 0),  # pro - желтый
            4: (255, 0, 255)   # non - пурпурный
        }

        if st.button("Распознать дефекты", key="single_button_2"):

            if uploaded_image is not None:
                image = Image.open(uploaded_image)
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

                    st.image(annotated_image, caption='Изображение с аннотациями', use_column_width=True)

                    if unique_classes:
                        unique_classes_str = ', '.join(unique_classes)
                        st.text(f"Дефекты на изображении: {unique_classes_str}")

                        st.markdown(
                            f"<span style='color:yellow'>{'Рекомендации:'}</span>",
                            unsafe_allow_html=True
                        )
                        recommendations = get_recommendations(unique_classes)
                        
                        for cls, rec in recommendations.items():
                            st.text_area(f"Рекомендации для {cls}", rec, height=100)
                    else:
                        st.text("Дефекты отсутствуют")
                else:
                    st.error("Ошибка при получении аннотаций от API.")
            else:
                st.error("Пожалуйста, загрузите изображение.")
if __name__ == "__main__":
    main()
