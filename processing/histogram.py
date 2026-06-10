import cv2
import numpy as np


def compute_grayscale_histogram(cv_image, bins=256):
    """Calcula o histograma em tons de cinza da imagem fornecida."""
    if len(cv_image.shape) == 3:
        gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = cv_image

    histogram = cv2.calcHist([gray_image], [0], None, [bins], [0, 256])
    return histogram.flatten()


def render_grayscale_histogram(cv_image, width=512, height=300, bins=256):
    """Desenha o histograma em uma imagem OpenCV pronta para exibição."""
    histogram = compute_grayscale_histogram(cv_image, bins=bins)
    canvas = np.full((height, width, 3), 255, dtype=np.uint8)

    if histogram.max() > 0:
        normalized_histogram = histogram / histogram.max()
    else:
        normalized_histogram = histogram

    padding = 24
    plot_width = width - (padding * 2)
    plot_height = height - (padding * 2)
    x_positions = np.linspace(padding, padding + plot_width - 1, num=bins)
    y_positions = height - padding - (normalized_histogram * plot_height)

    points = np.array(
        [[int(x_coord), int(y_coord)] for x_coord, y_coord in zip(x_positions, y_positions)],
        dtype=np.int32
    )

    cv2.rectangle(canvas, (padding, padding), (width - padding, height - padding), (220, 220, 220), 1)
    if len(points) > 1:
        cv2.polylines(canvas, [points.reshape((-1, 1, 2))], False, (40, 40, 40), 2)

    cv2.putText(canvas, "0", (padding - 8, height - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (90, 90, 90), 1)
    cv2.putText(canvas, "255", (width - padding - 18, height - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (90, 90, 90), 1)
    cv2.putText(canvas, "Histograma", (padding, 16), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (70, 70, 70), 1)

    return canvas