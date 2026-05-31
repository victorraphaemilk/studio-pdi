import cv2

def apply_mean_filter(cv_image, kernel_size=5):
    """Filtro da média: substitui o pixel pela média da vizinhança[cite: 91, 108]."""
    return cv2.blur(cv_image, (kernel_size, kernel_size))

def apply_gaussian_filter(cv_image, kernel_size=5):
    """Filtro gaussiano: suaviza com ponderação espacial (maior peso ao centro)[cite: 92, 108]."""
    # O kernel gaussiano exige um tamanho ímpar
    if kernel_size % 2 == 0: kernel_size += 1
    return cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)

def apply_median_filter(cv_image, kernel_size=5):
    """Filtro da mediana: reduz ruído impulsivo usando o valor mediano[cite: 93, 108]."""
    if kernel_size % 2 == 0: kernel_size += 1
    return cv2.medianBlur(cv_image, kernel_size)