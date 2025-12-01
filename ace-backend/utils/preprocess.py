import cv2
import numpy as np
from tensorflow.keras.applications.xception import preprocess_input

IMG_SIZE = (299, 299)

def prepare_image(image):
    # Use center crop instead of face detection
    h, w = image.shape[:2]
    s = min(h, w)
    crop = image[h//2-s//2:h//2+s//2, w//2-s//2:w//2+s//2]

    crop = cv2.resize(crop, IMG_SIZE)
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2RGB)
    crop = crop.astype("float32")
    crop = preprocess_input(crop)
    crop = np.expand_dims(crop, axis=0)
    return crop
