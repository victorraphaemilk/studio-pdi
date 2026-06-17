import tkinter as tk
from PIL import ImageTk

from processing.histogram import render_grayscale_histogram
from utils.image_handler import cv_to_pil

BG_SKY = "#D0F4F7"       
BG_WOOD = "#F2D8B1"      
FG_TEXT = "#4A3B32"      

class HistogramDialog(tk.Toplevel):
    def __init__(self, parent, on_close=None):
        super().__init__(parent)
        self.on_close = on_close
        self.tk_histogram_image = None

        self.title("🍄 Histograma do Processamento 🍁")
        self.geometry("560x420") 
        self.resizable(False, False)
        
        self.configure(bg=BG_SKY)
        self.transient(parent)

        self.status_label = tk.Label(
            self,
            text="Aplique uma magia (filtro) para visualizar a distribuição em cinza.",
            bg=BG_SKY,
            fg=FG_TEXT,
            font=("Arial", 11, "bold")
        )
        self.status_label.pack(padx=12, pady=(15, 10))

        self.image_frame = tk.Frame(
            self, 
            bg="white", 
            highlightthickness=4, 
            highlightbackground=BG_WOOD, 
            bd=0
        )
        self.image_frame.pack(padx=20, pady=(0, 20), fill=tk.BOTH, expand=True)

        self.image_label = tk.Label(self.image_frame, bg="white")
        self.image_label.pack(fill=tk.BOTH, expand=True)

        self.protocol("WM_DELETE_WINDOW", self.close)

    def update_histogram(self, cv_image):
        histogram_cv = render_grayscale_histogram(cv_image)
        histogram_pil = cv_to_pil(histogram_cv)

        self.tk_histogram_image = ImageTk.PhotoImage(histogram_pil)
        self.image_label.config(image=self.tk_histogram_image)
        self.status_label.config(text="Distribuição atual dos níveis de cinza (Poder da Imagem).")

    def clear_histogram(self):
        self.tk_histogram_image = None
        self.image_label.config(image="")
        self.status_label.config(text="Aplique uma magia (filtro) para visualizar a distribuição em cinza.")

    def close(self):
        if self.on_close:
            self.on_close()
        self.destroy()