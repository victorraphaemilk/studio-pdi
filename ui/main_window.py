import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from utils.image_handler import load_image, pil_to_cv, cv_to_pil
from processing.filters import apply_mean_filter, apply_mean_filter_numpy, apply_gaussian_filter, apply_median_filter
from processing.enhancement import apply_brightness_contrast
from processing.edge_detection import apply_laplacian_edge_detection
from ui.dialogs import HistogramDialog

BG_SKY = "#D0F4F7"      
BG_WOOD = "#F2D8B1"      
FG_TEXT = "#4A3B32"      
BTN_ACCENT = "#FF9966"   
BTN_HOVER = "#FFB380"   

class StudioPDIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍄 Studio PDI  🍁")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG_SKY)

        
        self.original_image = None
        self.tk_original_image = None
        self.processed_image = None
        self.processed_cv_image = None
        self.tk_processed_image = None
        self.current_filter = None
        self.histogram_dialog = None

        self.kernel_value = tk.IntVar(value=5)
        self.brightness_value = tk.IntVar(value=0)
        self.contrast_value = tk.DoubleVar(value=1.0)
        self.laplacian_kernel_value = tk.IntVar(value=3)

        
        self.container = tk.Frame(self.root, bg=BG_SKY)
        self.container.pack(fill=tk.BOTH, expand=True)

        
        self.setup_intro_screen()
        self.setup_main_ui()

        
        self.show_intro()

    def setup_intro_screen(self):
        
        self.intro_frame = tk.Frame(self.container, bg=BG_SKY)
        
        
        title_label = tk.Label(
            self.intro_frame, text="🍄 STUDIO PDI 🍄", 
            font=("Arial Rounded MT Bold", 40, "bold"), bg=BG_SKY, fg=FG_TEXT
        )
        title_label.pack(pady=(150, 10))

        
        subtitle = tk.Label(
            self.intro_frame, text="Carregue sua imagem para iniciar a aventura.",
            font=("Arial", 16), bg=BG_SKY, fg=FG_TEXT
        )
        subtitle.pack(pady=(0, 60))

        
        start_btn = tk.Button(
            self.intro_frame, text="START (Selecionar Imagem)", 
            font=("Arial Rounded MT Bold", 14, "bold"), bg=BTN_ACCENT, fg="white",
            activebackground=BTN_HOVER, relief="flat", padx=30, pady=15,
            cursor="hand2", command=self.open_file_and_start
        )
        start_btn.pack()

    def setup_main_ui(self):
        
        self.app_frame = tk.Frame(self.container, bg=BG_SKY)

        
        self.menubar = tk.Menu(self.root, bg=BG_WOOD, fg=FG_TEXT, activebackground=BTN_ACCENT)

        file_menu = tk.Menu(self.menubar, tearoff=0, bg=BG_WOOD, fg=FG_TEXT)
        file_menu.add_command(label="Abrir Nova Imagem", command=self.open_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        self.menubar.add_cascade(label="Arquivo", menu=file_menu)

        filter_menu = tk.Menu(self.menubar, tearoff=0, bg=BG_WOOD, fg=FG_TEXT)
        filter_menu.add_command(label="Média (CV2)", command=lambda: self.set_filter("media"))
        filter_menu.add_command(label="Média (NumPy)", command=lambda: self.set_filter("media_numpy"))
        filter_menu.add_command(label="Gaussiano", command=lambda: self.set_filter("gaussiano"))
        filter_menu.add_command(label="Mediana", command=lambda: self.set_filter("mediana"))
        self.menubar.add_cascade(label="Filtros (Suavização)", menu=filter_menu)

        enhancement_menu = tk.Menu(self.menubar, tearoff=0, bg=BG_WOOD, fg=FG_TEXT)
        enhancement_menu.add_command(label="Brilho e Contraste", command=lambda: self.set_filter("realce"))
        self.menubar.add_cascade(label="Realce", menu=enhancement_menu)

        edge_menu = tk.Menu(self.menubar, tearoff=0, bg=BG_WOOD, fg=FG_TEXT)
        edge_menu.add_command(label="Laplaciano", command=lambda: self.set_filter("laplaciano"))
        self.menubar.add_cascade(label="Bordas", menu=edge_menu)

        analysis_menu = tk.Menu(self.menubar, tearoff=0, bg=BG_WOOD, fg=FG_TEXT)
        analysis_menu.add_command(label="Histograma da Processada", command=self.open_histogram_dialog)
        self.menubar.add_cascade(label="Análise", menu=analysis_menu)

        
        self.main_content = tk.Frame(self.app_frame, bg=BG_SKY)
        self.main_content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.canvas_original = tk.Canvas(self.main_content, bg="white", highlightthickness=4, highlightbackground=BG_WOOD, bd=0)
        self.canvas_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        self.canvas_processed = tk.Canvas(self.main_content, bg="white", highlightthickness=4, highlightbackground=BG_WOOD, bd=0)
        self.canvas_processed.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10)

        self.control_frame = tk.Frame(self.app_frame, bg=BG_WOOD, pady=15, highlightthickness=3, highlightbackground="#D7B586")
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=20, pady=15)

        self.control_title = tk.Label(
            self.control_frame, text="Selecione um processamento no menu para habilitar os controles.",
            font=("Arial", 11, "bold"), bg=BG_WOOD, fg=FG_TEXT
        )
        self.control_title.pack()

        slider_opts = {'bg': BG_WOOD, 'fg': FG_TEXT, 'highlightthickness': 0, 'troughcolor': BG_SKY, 'orient': tk.HORIZONTAL, 'length': 300, 'font': ("Arial", 10)}

        self.kernel_controls = tk.Frame(self.control_frame, bg=BG_WOOD)
        self.kernel_slider = tk.Scale(
            self.kernel_controls, label="Tamanho do Kernel (Ímpar)", from_=1, to=51, resolution=2,
            variable=self.kernel_value, command=self.update_filter_realtime, **slider_opts
        )
        self.kernel_slider.pack()

        self.enhancement_controls = tk.Frame(self.control_frame, bg=BG_WOOD)
        self.brightness_slider = tk.Scale(
            self.enhancement_controls, label="Brilho", from_=-100, to=100,
            variable=self.brightness_value, command=self.update_filter_realtime, **slider_opts
        )
        self.brightness_slider.pack(side=tk.LEFT, padx=20)

        self.contrast_slider = tk.Scale(
            self.enhancement_controls, label="Contraste", from_=0.5, to=3.0, resolution=0.1,
            variable=self.contrast_value, command=self.update_filter_realtime, **slider_opts
        )
        self.contrast_slider.pack(side=tk.LEFT, padx=20)

        self.edge_controls = tk.Frame(self.control_frame, bg=BG_WOOD)
        self.laplacian_slider = tk.Scale(
            self.edge_controls, label="Kernel do Laplaciano (Ímpar)", from_=1, to=7, resolution=2,
            variable=self.laplacian_kernel_value, command=self.update_filter_realtime, **slider_opts
        )
        self.laplacian_slider.pack()

        self.update_control_visibility()

    def show_intro(self):
        self.app_frame.pack_forget()
        self.intro_frame.pack(fill=tk.BOTH, expand=True)
        self.root.config(menu="")

    def show_main(self):
        self.intro_frame.pack_forget()
        self.app_frame.pack(fill=tk.BOTH, expand=True)
        self.root.config(menu=self.menubar)

    def open_file_and_start(self):
        if self.process_open_file():
            self.show_main()

    def open_file_dialog(self):
        self.process_open_file()

    def process_open_file(self):
        filetypes = [("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todos", "*.*")]
        filepath = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=filetypes)

        if filepath:
            self.original_image = load_image(filepath)
            if self.original_image:
                self.current_filter = None
                self.processed_image = None
                self.processed_cv_image = None
                self.reset_controls()
                self.update_control_visibility()
                self.root.update_idletasks() 
                self.display_original_image()
                self.canvas_processed.delete("all")
                self.clear_histogram_dialog()
                return True
            else:
                messagebox.showerror("Erro", "Não foi possível abrir a imagem.")
        return False

    
    def display_original_image(self):
        canvas_width = self.canvas_original.winfo_width()
        canvas_height = self.canvas_original.winfo_height()

        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width - 10, canvas_height - 10))

        self.canvas_original.delete("all")
        self.tk_original_image = ImageTk.PhotoImage(img_copy)
        self.canvas_original.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_original_image
        )

    def display_processed_image(self):
        canvas_width = self.canvas_processed.winfo_width()
        canvas_height = self.canvas_processed.winfo_height()

        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.processed_image.copy()
        img_copy.thumbnail((canvas_width - 10, canvas_height - 10))

        self.canvas_processed.delete("all")
        self.tk_processed_image = ImageTk.PhotoImage(img_copy)
        self.canvas_processed.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_processed_image
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
        self.edge_controls.pack_forget()

        if self.current_filter in {"media", "media_numpy", "gaussiano", "mediana"}:
            self.control_title.config(text="Ajuste a força (Kernel) da sua magia de suavização.")
            self.kernel_controls.pack()
        elif self.current_filter == "realce":
            self.control_title.config(text="Ajuste o brilho e contraste.")
            self.enhancement_controls.pack()
        elif self.current_filter == "laplaciano":
            self.control_title.config(text="Ajuste a sensibilidade das bordas (Laplaciano).")
            self.edge_controls.pack()
        else:
            self.control_title.config(text="Selecione um processamento no menu acima.")

    def reset_controls(self):
        self.kernel_value.set(5)
        self.laplacian_kernel_value.set(3)
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
        elif self.current_filter == "media_numpy":
            kernel_size = self.kernel_slider.get()
            processed_cv = apply_mean_filter_numpy(cv_img, kernel_size)
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
        elif self.current_filter == "laplaciano":
            kernel_size = self.laplacian_slider.get()
            processed_cv = apply_laplacian_edge_detection(cv_img, kernel_size)
        else:
            return

        self.processed_cv_image = processed_cv
        self.processed_image = cv_to_pil(processed_cv)
        self.display_processed_image()
        self.refresh_histogram_dialog()

    
    def open_histogram_dialog(self):
        if self.processed_cv_image is None:
            messagebox.showwarning("Aviso", "Aplique um processamento antes de abrir o histograma.")
            return

        if self.histogram_dialog and self.histogram_dialog.winfo_exists():
            self.histogram_dialog.focus_force()
        else:
            self.histogram_dialog = HistogramDialog(self.root, on_close=self.handle_histogram_dialog_close)

        self.refresh_histogram_dialog()

    def refresh_histogram_dialog(self):
        if self.processed_cv_image is None:
            return

        if self.histogram_dialog and self.histogram_dialog.winfo_exists():
            self.histogram_dialog.update_histogram(self.processed_cv_image)

    def clear_histogram_dialog(self):
        if self.histogram_dialog and self.histogram_dialog.winfo_exists():
            self.histogram_dialog.clear_histogram()

    def handle_histogram_dialog_close(self):
        self.histogram_dialog = None