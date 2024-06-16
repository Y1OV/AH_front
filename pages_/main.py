import pandas as pd
import streamlit as st
import cv2
import numpy as np
import requests
import json
from PIL import Image

from funcc.risovashka import draw_bounding_box, visualize_annotations
from funcc.ostalnoe import get_recommendations, process_zip_file

# HTML-код для логотипа
html_code = '''
<div style="text-align: center;">
    <a href="https://raw.githubusercontent.com/Y1OV/DFO_front/main/lct/rosatom-logo-brandlogos.net.png">
        <img src="https://raw.githubusercontent.com/Y1OV/DFO_front/main/lct/rosatom-logo-brandlogos.net.png" alt="Foo" style="width: 50%; height: auto;">
    </a>
</div>
'''



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

                addr = 'https://086a-83-143-66-61.ngrok-free.app'
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
