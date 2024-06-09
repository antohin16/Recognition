from ultralytics import YOLO
from PIL import Image

# Пути к моделям - адаптируйте в соответствии с вашей структурой
FACTORY_MODEL_PATH = "/home/quvi/PycharmProjects/app/runs/detect/train3/weights/best.pt"
WATER_MODEL_PATH = "/home/quvi/PycharmProjects/app/runs/detect/train/weights/best.pt"

factory_model = YOLO(FACTORY_MODEL_PATH)
water_model = YOLO(WATER_MODEL_PATH)


def process_image(image_path):
    try:
        img = Image.open(image_path)

        # Определение показаний заводского счетчика
        factory_class_mapping = {
            0: '1', 1: '2', 2: '3', 3: '4', 4: '5', 5: '6',
            6: '7', 7: '8', 8: '9', 9: '0', 10: '.'
        }
        factory_confidence_threshold = 0.4
        factory_results = factory_model(img)
        factory_reading = extract_reading(factory_results, factory_class_mapping, factory_confidence_threshold)

        # Определение показаний водяного счетчика
        water_class_mapping = {
            0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5',
            6: '6', 7: '7', 8: '8', 9: '9'
        }
        water_confidence_threshold = 0.1
        water_results = water_model(img)
        water_reading = extract_reading(water_results, water_class_mapping, water_confidence_threshold)

        return factory_reading, water_reading
    except Exception as e:
        print(f"Error in process_image: {e}")
        return "Ошибка при обработке изображения"


def extract_reading(results, class_mapping, confidence_threshold):
    detected_classes = []
    for detection in results[0].boxes:
        x1, y1, x2, y2 = detection.xyxy[0]  # Координаты ограничивающего прямоугольника
        conf = detection.conf[0]  # Доверие
        cls = detection.cls[0]  # Класс

        if conf > confidence_threshold and int(cls) in class_mapping:
            detected_class = class_mapping[int(cls)]
            detected_classes.append((x1.item(), detected_class))

    detected_classes_sorted = sorted(detected_classes, key=lambda x: x[0])
    final_reading = ''.join([cls for _, cls in detected_classes_sorted])
    print(f"Detected reading: {final_reading}")  # Отладочный вывод
    return final_reading
