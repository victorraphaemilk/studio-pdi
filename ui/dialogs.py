import tkinter as tk
from PIL import ImageTk

from processing.histogram import render_grayscale_histogram
from utils.image_handler import cv_to_pil


class HistogramDialog(tk.Toplevel):
	def __init__(self, parent, on_close=None):
		super().__init__(parent)
		self.on_close = on_close
		self.tk_histogram_image = None

		self.title("Histograma da Imagem Processada")
		self.geometry("560x380")
		self.resizable(False, False)
		self.transient(parent)

		self.status_label = tk.Label(
			self,
			text="Selecione um processamento para visualizar a distribuição em cinza."
		)
		self.status_label.pack(padx=12, pady=(12, 8))

		self.image_label = tk.Label(self, bg="white")
		self.image_label.pack(padx=12, pady=(0, 12), fill=tk.BOTH, expand=True)

		self.protocol("WM_DELETE_WINDOW", self.close)

	def update_histogram(self, cv_image):
		histogram_cv = render_grayscale_histogram(cv_image)
		histogram_pil = cv_to_pil(histogram_cv)

		self.tk_histogram_image = ImageTk.PhotoImage(histogram_pil)
		self.image_label.config(image=self.tk_histogram_image)
		self.status_label.config(text="Distribuição em tons de cinza da imagem processada atual.")

	def clear_histogram(self):
		self.tk_histogram_image = None
		self.image_label.config(image="")
		self.status_label.config(text="Selecione um processamento para visualizar a distribuição em cinza.")

	def close(self):
		if self.on_close:
			self.on_close()
		self.destroy()