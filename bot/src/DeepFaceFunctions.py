import cv2
import numpy as np

from TelegramBotConfig import detector_backend_model, verify_model
from deepface import DeepFace

def verify_in_photo(
        image1: np.ndarray, 
        image2: np.ndarray, 
        detector_backend: str = detector_backend_model, 
        model_name: str = verify_model
    ) -> dict:
    """
    Verify 2 face

    :param image1: np.ndarray. Base face
    :param image2: np.ndarray. Verifing face
    :param detector_backend: str. Used detector backend
    :param model_name: str. Used model deepface analyzed model

    :return: dict. Result of verifing
    """

    result = DeepFace.verify(image1, image2, detector_backend=detector_backend, model_name=model_name, enforce_detection=False)

    return result

def get_face_from_photo(
        image: np.ndarray,
        detector_backend: str = detector_backend_model
    ) -> np.ndarray:
    """
    Get image of face

    :param image: np.ndarray. Image with faces
    :param detector_backend: str. Used detector backend

    :return: np.ndarray. Image of face (if it in)
    """

    face_objs = DeepFace.extract_faces(image, detector_backend=detector_backend, enforce_detection=False)
    face_obj = face_objs[0]

    area = face_obj['facial_area']
    x, y, w, h = area['x'], area['y'], area['w'], area['h']

    face_image = image[y:y+h, x:x+w]
    return face_image


if __name__ == '__main__':
    image1 = cv2.imread(r'../data/0.jpg')
    image2 = cv2.imread(r'../data/1.jpg')

    result = verify_in_photo(image1, image2, 'yolov8', 'Facenet512')

    print(result)