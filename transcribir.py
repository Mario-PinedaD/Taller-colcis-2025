import whisper
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import time

class SubtituladorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Subtitulador Automático")
        self.root.geometry("600x450")
        self.root.resizable(True, True)
        
        # Variables
        self.archivo_seleccionado = tk.StringVar()
        self.modelo_seleccionado = tk.StringVar(value="small")
        self.progreso = tk.DoubleVar()
        self.transcribiendo = False
        
        # Configurar estilo
        self.setup_estilo()
        
        # Crear interfaz
        self.crear_interfaz()
        
    def setup_estilo(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configurar colores
        self.root.configure(bg='#f0f0f0')
        style.configure('TFrame', background='#f0f0f0')
        style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10), padding=6)
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Progress.Horizontal.TProgressbar', troughcolor='#ffffff', background='#4CAF50')
        
    def crear_interfaz(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        titulo = ttk.Label(main_frame, text="Subtitulador Automático", style='Title.TLabel')
        titulo.pack(pady=(0, 20))
        
        # Marco de selección de archivo
        file_frame = ttk.Frame(main_frame)
        file_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(file_frame, text="Archivo de audio/video:").pack(anchor=tk.W)
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.pack(fill=tk.X, pady=5)
        
        ttk.Entry(file_select_frame, textvariable=self.archivo_seleccionado).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(file_select_frame, text="Seleccionar", command=self.seleccionar_archivo).pack(side=tk.RIGHT)
        
        # Marco de selección de modelo
        model_frame = ttk.Frame(main_frame)
        model_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(model_frame, text="Modelo de Whisper:").pack(anchor=tk.W)
        
        modelos = ["tiny", "base", "small", "medium", "large"]
        model_combo = ttk.Combobox(model_frame, textvariable=self.modelo_seleccionado, values=modelos, state="readonly")
        model_combo.pack(fill=tk.X, pady=5)
        
        # Información de modelos
        info_text = """
        Modelos disponibles (mayor precisión = más recursos):
        - tiny: Más rápido, menos preciso
        - base: Equilibrio velocidad/precisión
        - small: Buen equilibrio
        - medium: Mayor precisión
        - large: Máxima precisión (requiere más RAM)
        """
        info_label = ttk.Label(main_frame, text=info_text, justify=tk.LEFT)
        info_label.pack(fill=tk.X, pady=10)
        
        # Botón de transcripción
        self.btn_transcribir = ttk.Button(main_frame, text="Generar Subtítulos", command=self.iniciar_transcripcion)
        self.btn_transcribir.pack(pady=10)
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progreso, maximum=100, style='Progress.Horizontal.TProgressbar')
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.status_label = ttk.Label(main_frame, text="Listo")
        self.status_label.pack(fill=tk.X)
        
        # Consola de salida
        ttk.Label(main_frame, text="Mensajes:").pack(anchor=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.pack(fill=tk.BOTH, expand=True)
        
        self.output_text = tk.Text(output_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scrollbar.set)
        
        self.output_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
    def seleccionar_archivo(self):
        tipos_archivo = [
            ("Archivos multimedia", "*.wav *.mp3 *.ogg *.flac *.m4a *.mp4 *.avi *.mov *.mkv *.wmv"),
            ("Todos los archivos", "*.*")
        ]
        
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo de audio o video",
            filetypes=tipos_archivo
        )
        
        if archivo:
            self.archivo_seleccionado.set(archivo)
            self.log(f"Archivo seleccionado: {archivo}")
            
    def log(self, mensaje):
        self.output_text.insert(tk.END, f"{mensaje}\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
        
    def iniciar_transcripcion(self):
        if not self.archivo_seleccionado.get():
            messagebox.showerror("Error", "Por favor, selecciona un archivo de audio o video.")
            return
            
        if self.transcribiendo:
            return
            
        # Iniciar transcripción en un hilo separado
        self.transcribiendo = True
        self.btn_transcribir.config(state=tk.DISABLED)
        self.progreso.set(0)
        
        thread = threading.Thread(target=self.transcribir_audio)
        thread.daemon = True
        thread.start()
        
    def transcribir_audio(self):
        try:
            archivo = self.archivo_seleccionado.get()
            modelo = self.modelo_seleccionado.get()
            
            self.log(f"Cargando modelo {modelo}...")
            model = whisper.load_model(modelo)
            
            self.log("Transcribiendo audio (esto puede tomar varios minutos)...")
            
            # Simular progreso (Whisper no tiene callback de progreso nativo)
            def simular_progreso():
                while self.transcribiendo and self.progreso.get() < 90:
                    time.sleep(0.5)
                    self.progreso.set(self.progreso.get() + 1)
            
            progress_thread = threading.Thread(target=simular_progreso)
            progress_thread.daemon = True
            progress_thread.start()
            
            # Realizar la transcripción
            resultado = model.transcribe(archivo)
            
            # Generar nombre de archivo para los subtítulos
            nombre_base = os.path.splitext(archivo)[0]
            archivo_srt = f"{nombre_base}_subtitulos.srt"
            
            # Guardar como SRT
            with open(archivo_srt, "w", encoding="utf-8") as f:
                for i, segmento in enumerate(resultado["segments"], start=1):
                    inicio = segmento["start"]
                    fin = segmento["end"]
                    
                    # Convertir tiempos a formato SRT
                    def formato(t):
                        horas = int(t // 3600)
                        minutos = int((t % 3600) // 60)
                        segundos = int(t % 60)
                        milis = int((t % 1) * 1000)
                        return f"{horas:02}:{minutos:02}:{segundos:02},{milis:03}"
                    
                    f.write(f"{i}\n")
                    f.write(f"{formato(inicio)} --> {formato(fin)}\n")
                    f.write(f"{segmento['text'].strip()}\n\n")
            
            self.progreso.set(100)
            self.log(f"✅ Subtítulos generados en: {archivo_srt}")
            messagebox.showinfo("Éxito", f"Subtítulos generados correctamente en:\n{archivo_srt}")
            
        except Exception as e:
            self.log(f"❌ Error: {str(e)}")
            messagebox.showerror("Error", f"Ocurrió un error durante la transcripción:\n{str(e)}")
            
        finally:
            self.transcribiendo = False
            self.btn_transcribir.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = SubtituladorApp(root)
    root.mainloop()