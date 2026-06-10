import cv2


def apply_laplacian_edge_detection(cv_image, kernel_size=3):
	"""Aplica o operador Laplaciano e retorna a magnitude das bordas em cinza."""
	if kernel_size < 1:
		kernel_size = 1
	if kernel_size % 2 == 0:
		kernel_size += 1

	if len(cv_image.shape) == 3:
		gray_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
	else:
		gray_image = cv_image

	laplacian = cv2.Laplacian(gray_image, cv2.CV_16S, ksize=kernel_size)
	return cv2.convertScaleAbs(laplacian)