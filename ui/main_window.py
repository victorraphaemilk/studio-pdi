import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from utils.image_handler import load_image, pil_to_cv, cv_to_pil
from processing.filters import apply_mean_filter, apply_gaussian_filter, apply_median_filter
from processing.enhancement import apply_brightness_contrast


class StudioPDIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studio PDI - Processamento de Imagens")
        self.root.geometry("1000x650")

        self.original_image = None
        self.tk_original_image = None
        self.processed_image = None
        self.tk_processed_image = None
        self.current_filter = None

        self.kernel_value = tk.IntVar(value=5)
        self.brightness_value = tk.IntVar(value=0)
        self.contrast_value = tk.DoubleVar(value=1.0)

        self.setup_ui()

    def setup_ui(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir Imagem", command=self.open_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        filter_menu = tk.Menu(menubar, tearoff=0)
        filter_menu.add_command(label="Média", command=lambda: self.set_filter("media"))
        filter_menu.add_command(label="Gaussiano", command=lambda: self.set_filter("gaussiano"))
        filter_menu.add_command(label="Mediana", command=lambda: self.set_filter("mediana"))
        menubar.add_cascade(label="Filtros (Suavização)", menu=filter_menu)

        enhancement_menu = tk.Menu(menubar, tearoff=0)
        enhancement_menu.add_command(label="Brilho e Contraste", command=lambda: self.set_filter("realce"))
        menubar.add_cascade(label="Realce", menu=enhancement_menu)

        self.root.config(menu=menubar)

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas_original = tk.Canvas(self.main_frame, bg="gray")
        self.canvas_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.canvas_processed = tk.Canvas(self.main_frame, bg="darkgray")
        self.canvas_processed.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        self.control_frame = tk.Frame(self.root, pady=10)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.control_title = tk.Label(
            self.control_frame,
            text="Selecione um processamento para habilitar os controles."
        )
        self.control_title.pack()

        self.kernel_controls = tk.Frame(self.control_frame)
        self.kernel_slider = tk.Scale(
            self.kernel_controls,
            label="Tamanho do Kernel (Ímpar)",
            from_=1, to=51, resolution=2,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.kernel_value,
            command=self.update_filter_realtime
        )
        self.kernel_slider.pack()

        self.enhancement_controls = tk.Frame(self.control_frame)
        self.brightness_slider = tk.Scale(
            self.enhancement_controls,
            label="Brilho",
            from_=-100,
            to=100,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.brightness_value,
            command=self.update_filter_realtime
        )
        self.brightness_slider.pack(side=tk.LEFT, padx=10)

        self.contrast_slider = tk.Scale(
            self.enhancement_controls,
            label="Contraste",
            from_=0.5,
            to=3.0,
            resolution=0.1,
            orient=tk.HORIZONTAL,
            length=300,
            variable=self.contrast_value,
            command=self.update_filter_realtime
        )
        self.contrast_slider.pack(side=tk.LEFT, padx=10)

        self.update_control_visibility()

    def open_file_dialog(self):
        filetypes = [("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todos", "*.*")]
        filepath = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=filetypes)

        if filepath:
            self.original_image = load_image(filepath)
            if self.original_image:
                self.current_filter = None
                self.processed_image = None
                self.reset_controls()
                self.update_control_visibility()
                self.display_original_image()
                self.canvas_processed.delete("all")
            else:
                messagebox.showerror("Erro", "Não foi possível abrir a imagem.")

    def display_original_image(self):
        canvas_width = self.canvas_original.winfo_width()
        canvas_height = self.canvas_original.winfo_height()

        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height))

        self.canvas_original.delete("all")
        self.tk_original_image = ImageTk.PhotoImage(img_copy)
        self.canvas_original.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_original_image
        )

    def set_filter(self, filter_type):
        if not self.original_image:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return

        self.current_filter = filter_type
        if self.current_filter == "realce":
            self.reset_enhancement_controls()
        self.update_control_visibility()
        self.update_filter_realtime()

    def update_control_visibility(self):
        self.kernel_controls.pack_forget()
        self.enhancement_controls.pack_forget()

        if self.current_filter in {"media", "gaussiano", "mediana"}:
            self.control_title.config(text="Ajuste o kernel do filtro selecionado.")
            self.kernel_controls.pack()
        elif self.current_filter == "realce":
            self.control_title.config(text="Ajuste brilho e contraste sobre a imagem original.")
            self.enhancement_controls.pack()
        else:
            self.control_title.config(text="Selecione um processamento para habilitar os controles.")

    def reset_controls(self):
        self.kernel_value.set(5)
        self.reset_enhancement_controls()

    def reset_enhancement_controls(self):
        self.brightness_value.set(0)
        self.contrast_value.set(1.0)

    def update_filter_realtime(self, *args):
        if not self.original_image or not self.current_filter:
            return

        cv_img = pil_to_cv(self.original_image)

        if self.current_filter == "media":
            kernel_size = self.kernel_slider.get()
            processed_cv = apply_mean_filter(cv_img, kernel_size)
        elif self.current_filter == "gaussiano":
            kernel_size = self.kernel_slider.get()
            processed_cv = apply_gaussian_filter(cv_img, kernel_size)
        elif self.current_filter == "mediana":
            kernel_size = self.kernel_slider.get()
            processed_cv = apply_median_filter(cv_img, kernel_size)
        elif self.current_filter == "realce":
            brightness = self.brightness_slider.get()
            contrast = self.contrast_slider.get()
            processed_cv = apply_brightness_contrast(cv_img, brightness, contrast)
        else:
            return

        self.processed_image = cv_to_pil(processed_cv)
        self.display_processed_image()

    def display_processed_image(self):
        canvas_width = self.canvas_processed.winfo_width()
        canvas_height = self.canvas_processed.winfo_height()

        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.processed_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height))

        self.canvas_processed.delete("all")
        self.tk_processed_image = ImageTk.PhotoImage(img_copy)
        self.canvas_processed.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_processed_image
        )