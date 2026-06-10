import cv2
import numpy as np



def apply_mean_filter(cv_image, kernel_size=5):
    """Substitui cada pixel pela média da vizinhança."""
    return cv2.blur(cv_image, (kernel_size, kernel_size))

def apply_mean_filter_numpy(image, kernel_size=5):
    """Substitui cada pixel pela média da vizinhança usando apenas NumPy."""
    
    img_array = np.array(image, dtype=np.float32)
    
    is_grayscale = len(img_array.shape) == 2
    if is_grayscale:
        img_array = img_array[:, :, np.newaxis]
        
    altura, largura, canais = img_array.shape
    pad = kernel_size // 2
    resultado = np.zeros_like(img_array)
    img_padded = np.pad(img_array, ((pad, pad), (pad, pad), (0, 0)), mode='edge')

    for y in range(altura):
        for x in range(largura):
            for c in range(canais):
                # Extrai a "fatia" da matriz correspondente à vizinhança
                vizinhanca = img_padded[y : y + kernel_size, x : x + kernel_size, c]
                
                # Calcula a média dessa região e atribui ao pixel central
                resultado[y, x, c] = np.mean(vizinhanca)
                
    if is_grayscale:
        resultado = resultado.reshape((altura, largura))
        
    # Converte de volta para inteiros de 8 bits (padrão de imagem)
    return np.clip(resultado, 0, 255).astype(np.uint8)


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