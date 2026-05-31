import numpy as np


def apply_brightness_contrast(cv_image, brightness=0, contrast=1.0):
    """Aplica ajuste linear de brilho e contraste em imagem OpenCV."""
    adjusted_image = cv_image.astype(np.float32) * float(contrast) + float(brightness)
    return np.clip(adjusted_image, 0, 255).astype(np.uint8)
