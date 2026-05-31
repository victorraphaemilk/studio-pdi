import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import ImageTk
from utils.image_handler import load_image, pil_to_cv, cv_to_pil
from processing.filters import apply_mean_filter, apply_gaussian_filter, apply_median_filter

class StudioPDIApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Studio PDI - Processamento de Imagens")
        self.root.geometry("1000x650") # Aumentei um pouco a altura para caber o slider

        # Variáveis de estado
        self.original_image = None
        self.tk_original_image = None
        self.processed_image = None
        self.tk_processed_image = None
        
        # Guarda qual filtro está selecionado no momento
        self.current_filter = None 

        self.setup_ui()

    def setup_ui(self):
        # 1. Menu Superior
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

        self.root.config(menu=menubar)

        # 2. Frame Principal para imagens (Lado a Lado)
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.canvas_original = tk.Canvas(self.main_frame, bg="gray")
        self.canvas_original.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        self.canvas_processed = tk.Canvas(self.main_frame, bg="darkgray")
        self.canvas_processed.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

        # 3. NOVO: Frame Inferior para Controles
        self.control_frame = tk.Frame(self.root, pady=10)
        self.control_frame.pack(fill=tk.X, side=tk.BOTTOM)

        # Slider de Kernel (de 1 a 51, pulando de 2 em 2 para garantir números ímpares)
        self.kernel_slider = tk.Scale(
            self.control_frame, 
            label="Tamanho do Kernel (Ímpar)", 
            from_=1, to=51, resolution=2, 
            orient=tk.HORIZONTAL, 
            length=300,
            command=self.update_filter_realtime # Chama esta função sempre que o slider mover
        )
        self.kernel_slider.set(20) # Valor padrão
        self.kernel_slider.pack()

    def open_file_dialog(self):
        filetypes = [("Imagens", "*.jpg *.jpeg *.png *.bmp"), ("Todos", "*.*")]
        filepath = filedialog.askopenfilename(title="Selecione uma imagem", filetypes=filetypes)

        if filepath:
            self.original_image = load_image(filepath)
            if self.original_image:
                self.current_filter = None # Reseta o filtro ao carregar nova imagem
                self.display_original_image()
                # Limpa o canvas da imagem processada
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

        self.tk_original_image = ImageTk.PhotoImage(img_copy)
        self.canvas_original.create_image(
            canvas_width//2, canvas_height//2,
            anchor=tk.CENTER, image=self.tk_original_image
        )

    # NOVO: Define qual filtro está ativo e dispara a primeira atualização
    def set_filter(self, filter_type):
        if not self.original_image:
            messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
            return
        
        self.current_filter = filter_type
        self.update_filter_realtime()

    # NOVO: Aplica o processamento baseado no valor atual do slider
    def update_filter_realtime(self, *args):
        # O Tkinter passa argumentos pro 'command' do Scale, por isso o *args
        if not self.original_image or not self.current_filter:
            return

        kernel_size = self.kernel_slider.get()
        cv_img = pil_to_cv(self.original_image)

        if self.current_filter == "media":
            processed_cv = apply_mean_filter(cv_img, kernel_size)
        elif self.current_filter == "gaussiano":
            processed_cv = apply_gaussian_filter(cv_img, kernel_size)
        elif self.current_filter == "mediana":
            processed_cv = apply_median_filter(cv_img, kernel_size)

        self.processed_image = cv_to_pil(processed_cv)
        self.display_processed_image()

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