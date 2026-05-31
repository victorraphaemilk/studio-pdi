import cv2
import numpy as np
from PIL import Image

def load_image(filepath):
    """Abre a imagem a partir do caminho do arquivo."""
    try:
        return Image.open(filepath)
    except Exception as e:
        print(f"Erro ao carregar imagem: {e}")
        return None

def pil_to_cv(pil_image):
    """Converte imagem Pillow (RGB) para formato OpenCV (BGR/Numpy)."""
    cv_image = np.array(pil_image)
    # Se a imagem tiver 3 canais (cor), converte de RGB para BGR
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    return cv_image

def cv_to_pil(cv_image):
    """Converte imagem OpenCV (BGR/Numpy) de volta para Pillow (RGB)."""
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_image)