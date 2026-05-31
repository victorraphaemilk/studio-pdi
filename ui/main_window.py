import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from utils.image_handler import load_image, pil_to_cv, cv_to_pil
from processing.filters import apply_mean_filter, apply_gaussian_filter, apply_median_filter

class StudioPDIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studio PDI - Processamento de Imagens")
        self.root.geometry("1000x600")

        # Variáveis para armazenar as imagens
        self.original_image = None
        self.tk_original_image = None

        self.setup_ui()

    def setup_ui(self):
        menubar = tk.Menu(self.root)
        
        # Menu Arquivo (mantenha como estava)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Abrir Imagem", command=self.open_file_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)
        menubar.add_cascade(label="Arquivo", menu=file_menu)

        # NOVO: Menu Filtros
        filter_menu = tk.Menu(menubar, tearoff=0)
        filter_menu.add_command(label="Média", command=lambda: self.apply_filter("media"))
        filter_menu.add_command(label="Gaussiano", command=lambda: self.apply_filter("gaussiano"))
        filter_menu.add_command(label="Mediana", command=lambda: self.apply_filter("mediana"))
        menubar.add_cascade(label="Filtros (Suavização)", menu=filter_menu)

        self.root.config(menu=menubar)

        # ... (mantenha a criação do main_frame e dos canvas igual)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.canvas_original = tk.Canvas(self.main_frame, bg="gray")
        self.canvas_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.canvas_processed = tk.Canvas(self.main_frame, bg="darkgray")
        self.canvas_processed.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    def open_file_dialog(self):
        # Restringe aos formatos definidos no projeto
        filetypes = [
            ("Imagens", "*.jpg *.jpeg *.png *.bmp"),
            ("Todos os arquivos", "*.*")
        ]
        filepath = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=filetypes)

        if filepath:
            self.original_image = load_image(filepath)
            if self.original_image:
                self.display_original_image()
            else:
                messagebox.showerror("Erro", "Não foi possível abrir a imagem.")

    def display_original_image(self):
        # Redimensiona para caber no canvas (apenas para exibição, mantém a original intacta)
        canvas_width = self.canvas_original.winfo_width()
        canvas_height = self.canvas_original.winfo_height()

        # Evita erro caso o canvas ainda não tenha sido desenhado na tela
        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.original_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height))

        self.tk_original_image = ImageTk.PhotoImage(img_copy)
        self.canvas_original.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_original_image
        )

    def apply_filter(self, filter_type):
        if not self.original_image:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return

        # 1. Converte PIL (Interface) para OpenCV (Processamento)
        cv_img = pil_to_cv(self.original_image)

        # 2. Aplica o filtro selecionado (estamos usando kernel = 5 por enquanto)
        if filter_type == "media":
            processed_cv = apply_mean_filter(cv_img, kernel_size=50)
        elif filter_type == "gaussiano":
            processed_cv = apply_gaussian_filter(cv_img, kernel_size=50)
        elif filter_type == "mediana":
            processed_cv = apply_median_filter(cv_img, kernel_size=50)

        # 3. Converte de volta para PIL
        self.processed_image = cv_to_pil(processed_cv)

        # 4. Exibe no quadro da direita para comparar visualmente
        self.display_processed_image()

    # NOVO: Exibição da imagem processada
    def display_processed_image(self):
        canvas_width = self.canvas_processed.winfo_width()
        canvas_height = self.canvas_processed.winfo_height()

        if canvas_width <= 1: canvas_width = 450
        if canvas_height <= 1: canvas_height = 450

        img_copy = self.processed_image.copy()
        img_copy.thumbnail((canvas_width, canvas_height))

        self.tk_processed_image = ImageTk.PhotoImage(img_copy)
        self.canvas_processed.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_processed_image
        )

        