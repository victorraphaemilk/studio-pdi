import cv2


def apply_mean_filter(cv_image, kernel_size=5):
    """Substitui cada pixel pela média da vizinhança."""
    return cv2.blur(cv_image, (kernel_size, kernel_size))


def apply_gaussian_filter(cv_image, kernel_size=5):
    """Suaviza a imagem com maior peso para a região central."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)


def apply_median_filter(cv_image, kernel_size=5):
    """Reduz ruído impulsivo usando a mediana da vizinhança."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.medianBlur(cv_image, kernel_size)