# Studio PDI

## 1. Visão geral

O **Studio PDI** é uma aplicação desktop em **Python + Tkinter** para estudo de **Processamento Digital de Imagens**. A interface carrega uma imagem original no painel esquerdo, aplica uma operação no painel direito e mantém a separação entre:

1. **camada de interface**;
2. **camada de processamento**;
3. **camada de conversão de formatos**.

No estado atual do projeto, a aplicação oferece:

- filtros de suavização por **média**, **gaussiano** e **mediana**;
- controle de intensidade dos filtros espaciais por **slider de kernel**;
- modo de **realce por brilho e contraste** com dois sliders dedicados;
- processamento sempre refeito a partir da **imagem original**, evitando acúmulo de degradação.

---

## 2. Arquitetura atual

### 2.1 Estrutura de diretórios

| Caminho | Papel no projeto |
| --- | --- |
| `main.py` | Ponto de entrada da aplicação Tkinter. |
| `ui\main_window.py` | Janela principal, menus, canvas, sliders e orquestração do fluxo. |
| `processing\filters.py` | Filtros espaciais de suavização. |
| `processing\enhancement.py` | Ajuste linear de brilho e contraste. |
| `utils\image_handler.py` | Conversão entre Pillow e OpenCV, além de carga de imagem. |
| `processing\edge_detection.py` | Módulo reservado para futuras operações. |
| `ui\dialogs.py` | Módulo reservado para futuras janelas auxiliares. |

### 2.2 Fluxo da aplicação

O fluxo principal pode ser descrito assim:

1. `main.py` cria a raiz Tkinter.
2. `StudioPDIApp` monta a interface e inicializa o estado.
3. O usuário abre uma imagem por `open_file_dialog`.
4. A imagem é carregada em Pillow por `load_image`.
5. Ao selecionar um filtro ou mover um slider, `update_filter_realtime` converte a imagem para OpenCV, aplica a operação e converte o resultado de volta para Pillow.
6. A imagem processada é exibida no canvas da direita.

### 2.3 Diagrama textual

```text
main.py
  -> ui\main_window.py
       -> utils\image_handler.py
            -> load_image()
            -> pil_to_cv()
            -> cv_to_pil()
       -> processing\filters.py
            -> apply_mean_filter()
            -> apply_gaussian_filter()
            -> apply_median_filter()
       -> processing\enhancement.py
            -> apply_brightness_contrast()
```

---

## 3. Explicação do código por módulo

### 3.1 Entrada da aplicação

**Referência:** `main.py:1-7`

```python
import tkinter as tk
from ui.main_window import StudioPDIApp

if __name__ == "__main__":
    root = tk.Tk()
    app = StudioPDIApp(root)
    root.mainloop()
```

Esse arquivo existe para isolar o bootstrap da interface. Ele não contém regra de negócio; apenas cria a janela raiz e delega toda a lógica para `StudioPDIApp`.

### 3.2 Janela principal e estado da interface

**Referência:** `ui\main_window.py:9-26`

```python
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
```

Essa seção concentra o **estado da aplicação**:

- `original_image`: fonte imutável de processamento;
- `processed_image`: resultado mais recente;
- `current_filter`: modo ativo;
- `kernel_value`, `brightness_value`, `contrast_value`: estado dos controles.

O ponto mais importante dessa modelagem é a separação entre **imagem original** e **imagem processada**, porque ela impede o encadeamento acidental de perdas a cada ajuste em tempo real.

### 3.3 Montagem da interface

**Referência:** `ui\main_window.py:27-104`

```python
filter_menu = tk.Menu(menubar, tearoff=0)
filter_menu.add_command(label="Média", command=lambda: self.set_filter("media"))
filter_menu.add_command(label="Gaussiano", command=lambda: self.set_filter("gaussiano"))
filter_menu.add_command(label="Mediana", command=lambda: self.set_filter("mediana"))
menubar.add_cascade(label="Filtros (Suavização)", menu=filter_menu)

enhancement_menu = tk.Menu(menubar, tearoff=0)
enhancement_menu.add_command(label="Brilho e Contraste", command=lambda: self.set_filter("realce"))
menubar.add_cascade(label="Realce", menu=enhancement_menu)
```

O menu superior separa os grupos de operação por intenção:

- `Arquivo`: entrada e saída;
- `Filtros (Suavização)`: operações espaciais;
- `Realce`: transformação de brilho e contraste.

Mais abaixo, a interface define dois conjuntos de controles:

- `kernel_controls`, usado pelos filtros espaciais;
- `enhancement_controls`, usado pelo modo de realce.

Isso permitiu reutilizar a mesma área inferior sem misturar sliders de naturezas diferentes.

### 3.4 Carregamento e reset de estado

**Referência:** `ui\main_window.py:106-120`

```python
if filepath:
    self.original_image = load_image(filepath)
    if self.original_image:
        self.current_filter = None
        self.processed_image = None
        self.reset_controls()
        self.update_control_visibility()
        self.display_original_image()
        self.canvas_processed.delete("all")
```

Ao abrir uma nova imagem, a aplicação:

1. substitui a `original_image`;
2. remove o modo anteriormente selecionado;
3. restaura sliders para valores neutros;
4. limpa o painel processado.

Esse reset é importante para evitar que o novo arquivo herde o contexto visual da imagem anterior.

### 3.5 Seleção do modo e troca dinâmica dos controles

**Referência:** `ui\main_window.py:139-169`

```python
def set_filter(self, filter_type):
    if not self.original_image:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
        return

    self.current_filter = filter_type
    if self.current_filter == "realce":
        self.reset_enhancement_controls()
    self.update_control_visibility()
    self.update_filter_realtime()
```

```python
def update_control_visibility(self):
    self.kernel_controls.pack_forget()
    self.enhancement_controls.pack_forget()

    if self.current_filter in {"media", "gaussiano", "mediana"}:
        self.control_title.config(text="Ajuste o kernel do filtro selecionado.")
        self.kernel_controls.pack()
    elif self.current_filter == "realce":
        self.control_title.config(text="Ajuste brilho e contraste sobre a imagem original.")
        self.enhancement_controls.pack()
```

Aqui está o mecanismo que mantém a interface coerente:

- filtros espaciais exibem apenas o slider de kernel;
- o modo de realce exibe apenas brilho e contraste;
- ao entrar em realce, os valores voltam a neutro.

### 3.6 Pipeline de processamento em tempo real

**Referência:** `ui\main_window.py:171-194`

```python
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
```

Esse método é o centro da aplicação. Ele recebe tanto chamadas diretas quanto callbacks do `Scale`, por isso usa `*args`. O passo crítico é:

```python
cv_img = pil_to_cv(self.original_image)
```

Isso garante que qualquer mudança de slider sempre parta da **mesma base original**, em vez de reaplicar transformações sobre o último resultado.

### 3.7 Filtros de suavização

**Referência:** `processing\filters.py:1-18`

```python
def apply_gaussian_filter(cv_image, kernel_size=5):
    """Suaviza a imagem com maior peso para a região central."""
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(cv_image, (kernel_size, kernel_size), 0)
```

Os três filtros expõem uma interface simples e uniforme:

- `apply_mean_filter`: média local;
- `apply_gaussian_filter`: suavização ponderada;
- `apply_median_filter`: remoção de ruído impulsivo.

O ajuste para tamanho ímpar em gaussiano e mediana é necessário porque esses operadores dependem de um centro bem definido no kernel.

### 3.8 Conversão entre Pillow e OpenCV

**Referência:** `utils\image_handler.py:6-27`

```python
def pil_to_cv(pil_image):
    """Converte imagem Pillow (RGB) para formato OpenCV (BGR/Numpy)."""
    cv_image = np.array(pil_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    return cv_image
```

```python
def cv_to_pil(cv_image):
    """Converte imagem OpenCV (BGR/Numpy) de volta para Pillow (RGB)."""
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    return Image.fromarray(cv_image)
```

Tkinter exibe bem imagens via Pillow, enquanto OpenCV facilita o processamento. Esse módulo existe para centralizar a conversão e impedir que a UI conheça detalhes de canal RGB/BGR.

### 3.9 Realce de brilho e contraste

**Referência:** `processing\enhancement.py:4-7`

```python
def apply_brightness_contrast(cv_image, brightness=0, contrast=1.0):
    """Aplica ajuste linear de brilho e contraste em imagem OpenCV."""
    adjusted_image = cv_image.astype(np.float32) * float(contrast) + float(brightness)
    return np.clip(adjusted_image, 0, 255).astype(np.uint8)
```

Esse módulo implementa uma transformação linear por pixel:

```text
novo_valor = valor_original * contraste + brilho
```

Detalhes importantes:

- a imagem é convertida para `float32` antes da conta para evitar overflow durante a multiplicação;
- `np.clip` limita a saída no intervalo válido de 8 bits;
- o retorno volta para `uint8`, formato esperado pelo restante do pipeline.

---

## 4. Evolução do projeto por commit

### 4.1 `3287821` — Initial commit

**Resumo:** criação inicial do repositório com `LICENSE` e `README.md`.

**O que entrou:**

- estrutura mínima de versionamento;
- licença do projeto;
- README inicial ainda sem conteúdo técnico.

**Impacto arquitetural:** nenhum código de aplicação foi introduzido ainda; esse commit apenas abriu a base do repositório.

### 4.2 `d8ba4dc` — Implementacao estrutura e filtros espaciais

**Resumo:** primeiro commit funcional da aplicação.

**Arquivos centrais adicionados:**

- `main.py`
- `ui\main_window.py`
- `processing\filters.py`
- `utils\image_handler.py`
- módulos reservados `processing\enhancement.py`, `processing\edge_detection.py` e `ui\dialogs.py`

**O que foi implementado:**

1. criação da janela principal;
2. dois canvas para comparação lado a lado;
3. carregamento de imagem por seletor de arquivo;
4. filtros espaciais de média, gaussiano e mediana;
5. conversão Pillow/OpenCV;
6. primeiro pipeline de processamento e exibição.

**Trecho representativo do commit:**

**Referência histórica:** `d8ba4dc:ui/main_window.py`

```python
def apply_filter(self, filter_type):
    if not self.original_image:
        messagebox.showwarning("Aviso", "Carregue uma imagem primeiro.")
        return

    cv_img = pil_to_cv(self.original_image)

    if filter_type == "media":
        processed_cv = apply_mean_filter(cv_img, kernel_size=50)
    elif filter_type == "gaussiano":
        processed_cv = apply_gaussian_filter(cv_img, kernel_size=50)
    elif filter_type == "mediana":
        processed_cv = apply_median_filter(cv_img, kernel_size=50)
```

**Leitura técnica do commit:**

- a arquitetura já nascia em camadas;
- a UI ainda chamava um método único `apply_filter`;
- o kernel estava fixo, então o usuário trocava o tipo de filtro, mas não a intensidade.

### 4.3 `f2aef59` — Adicionada slide bar para intensidade do filtro

**Resumo:** o projeto saiu de filtros estáticos para filtros ajustáveis em tempo real.

**O que mudou:**

1. o método `apply_filter` foi substituído por um fluxo orientado a estado (`current_filter`);
2. foi introduzido um `Scale` para controlar o kernel;
3. o processamento passou a responder ao movimento do slider.

**Trecho representativo do commit:**

**Referência histórica:** `f2aef59:ui/main_window.py`

```python
self.kernel_slider = tk.Scale(
    self.control_frame,
    label="Tamanho do Kernel (Ímpar)",
    from_=1, to=51, resolution=2,
    orient=tk.HORIZONTAL,
    length=300,
    command=self.update_filter_realtime
)
```

```python
def update_filter_realtime(self, *args):
    if not self.original_image or not self.current_filter:
        return

    kernel_size = self.kernel_slider.get()
    cv_img = pil_to_cv(self.original_image)
```

**Leitura técnica do commit:**

- o projeto ganhou o conceito de **modo ativo**;
- o controle de intensidade passou a ser contínuo;
- a decisão de processar sempre a partir de `original_image` já começou a ficar explícita.

### 4.4 `5a12b88` — Adiciona filtros de realce e contraste

**Resumo:** o projeto incorporou um segundo grupo de operações, agora voltado a realce tonal.

**O que mudou:**

1. novo menu `Realce`;
2. novo módulo `processing\enhancement.py`;
3. sliders específicos para brilho e contraste;
4. troca dinâmica de controles conforme o modo ativo;
5. reset para valores neutros ao abrir nova imagem ou entrar em realce.

**Trecho representativo do commit:**

**Referência histórica:** `5a12b88:processing/enhancement.py`

```python
def apply_brightness_contrast(cv_image, brightness=0, contrast=1.0):
    adjusted_image = cv_image.astype(np.float32) * float(contrast) + float(brightness)
    return np.clip(adjusted_image, 0, 255).astype(np.uint8)
```

**Referência histórica:** `5a12b88:ui/main_window.py`

```python
elif self.current_filter == "realce":
    brightness = self.brightness_slider.get()
    contrast = self.contrast_slider.get()
    processed_cv = apply_brightness_contrast(cv_img, brightness, contrast)
```

**Leitura técnica do commit:**

- a UI deixou de ter um único tipo de controle;
- o rodapé passou a ser um contêiner dinâmico;
- o projeto consolidou a regra arquitetural de aplicar operações sempre sobre a imagem original.

---

## 5. O que cada parte do código resolve

| Parte | Problema resolvido | Onde está |
| --- | --- | --- |
| Bootstrap Tkinter | Inicializar a aplicação e a janela raiz | `main.py` |
| Estado da interface | Rastrear imagem original, resultado e modo ativo | `ui\main_window.py:9-26` |
| Menu de operações | Permitir seleção explícita do processamento | `ui\main_window.py:27-46` |
| Canvas lado a lado | Comparar entrada e saída visualmente | `ui\main_window.py:48-58` |
| Slider de kernel | Ajustar intensidade dos filtros espaciais | `ui\main_window.py:66-76` |
| Sliders de realce | Ajustar brilho e contraste em tempo real | `ui\main_window.py:78-104` |
| Troca dinâmica de controles | Mostrar apenas controles válidos para o modo ativo | `ui\main_window.py:150-161` |
| Filtros OpenCV | Executar a transformação da imagem | `processing\filters.py` |
| Realce linear | Ajustar ganho e offset tonal | `processing\enhancement.py` |
| Conversão Pillow/OpenCV | Fazer a ponte entre UI e processamento | `utils\image_handler.py` |

---

## 6. Desafios encontrados na evolução do projeto

### 6.1 Manter processamento não destrutivo

O maior cuidado técnico foi impedir que o usuário movesse sliders em cascata sobre uma imagem já modificada. A solução adotada foi sempre converter `self.original_image` para OpenCV no instante do processamento.

### 6.2 Conciliar Tkinter com OpenCV

Tkinter e OpenCV não trabalham com o mesmo formato de imagem por padrão. O projeto resolveu isso com um módulo dedicado de conversão, evitando espalhar lógica de canais RGB/BGR pela interface.

### 6.3 Kernel ímpar para filtros espaciais

Filtros gaussiano e mediano exigem centro definido. Por isso, mesmo que o usuário escolha um valor par, o código ajusta para o próximo ímpar antes da chamada ao OpenCV.

### 6.4 Controles heterogêneos na mesma interface

Quando o projeto só tinha filtros espaciais, um único slider resolvia a UX. Com a chegada do realce, foi necessário trocar dinamicamente os widgets exibidos no rodapé sem quebrar o fluxo existente.

### 6.5 Limites numéricos no realce

Brilho e contraste podem empurrar pixels para fora da faixa `0..255`. O uso de `float32` seguido de `np.clip(...).astype(np.uint8)` impede estouro numérico e garante compatibilidade com Pillow/OpenCV.

---

## 7. Estado atual do sistema

### 7.1 Funcionalidades disponíveis

- abertura de imagem por seletor de arquivo;
- visualização lado a lado;
- filtro da média com kernel variável;
- filtro gaussiano com kernel variável;
- filtro da mediana com kernel variável;
- realce por brilho e contraste com atualização em tempo real.

### 7.2 Limitações observadas

- `requirements.txt` ainda está vazio, apesar de o código depender de `Pillow`, `NumPy` e `OpenCV`;
- `processing\edge_detection.py` e `ui\dialogs.py` existem como espaços reservados, mas ainda não possuem implementação funcional;
- não há suíte automatizada de testes além da validação por compilação e execução da aplicação.

---

## 8. Trechos de código mais importantes para estudo

### 8.1 Regra de processamento sempre sobre a original

**Referência:** `ui\main_window.py:171-175`

```python
def update_filter_realtime(self, *args):
    if not self.original_image or not self.current_filter:
        return

    cv_img = pil_to_cv(self.original_image)
```

### 8.2 Aplicação do realce

**Referência:** `ui\main_window.py:186-189`

```python
elif self.current_filter == "realce":
    brightness = self.brightness_slider.get()
    contrast = self.contrast_slider.get()
    processed_cv = apply_brightness_contrast(cv_img, brightness, contrast)
```

### 8.3 Ajuste linear com saturação

**Referência:** `processing\enhancement.py:4-7`

```python
def apply_brightness_contrast(cv_image, brightness=0, contrast=1.0):
    adjusted_image = cv_image.astype(np.float32) * float(contrast) + float(brightness)
    return np.clip(adjusted_image, 0, 255).astype(np.uint8)
```

### 8.4 Conversão de RGB para BGR

**Referência:** `utils\image_handler.py:15-20`

```python
def pil_to_cv(pil_image):
    cv_image = np.array(pil_image)
    if len(cv_image.shape) == 3:
        cv_image = cv2.cvtColor(cv_image, cv2.COLOR_RGB2BGR)
    return cv_image
```

---
