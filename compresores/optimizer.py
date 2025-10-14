import os
from PIL import Image, ImageOps
import ffmpeg
import time
from tkinter import Tk, filedialog
from renombrarRegex import renombrarArchivos

"""
Es importante que el archivo de ffmpeg.zip se deba descomprimir y se añada al path en las variables del sistema
"""

def optimizar_archivos(carpeta, calidad_img=80, codec_video="libx265", crf=28, preset="medium"):
    """
    Optimiza imágenes y videos en una carpeta (y subcarpetas) de forma recursiva.
    Genera una nueva carpeta raíz con sufijo '-optimizados'.
    """

    carpeta_opt = carpeta.rstrip(os.sep) + "-optimizados"
    os.makedirs(carpeta_opt, exist_ok=True)

    # Extensiones
    #extensiones_img = (".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp")
    extensiones_img = (".jpg", ".png")
    extensiones_vid = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm")

    for ruta_actual, _, archivos in os.walk(carpeta):
        ruta_relativa = os.path.relpath(ruta_actual, carpeta)
        ruta_destino = os.path.join(carpeta_opt, ruta_relativa)
        os.makedirs(ruta_destino, exist_ok=True)

        for archivo in archivos:
            ruta_archivo = os.path.join(ruta_actual, archivo)
            nombre, ext = os.path.splitext(archivo)
            ext = ext.lower()

            # Procesar imágenes
            if ext in extensiones_img:
                nuevo_nombre = f"{nombre}_opt.jpeg"
                ruta_nueva = os.path.normpath(os.path.join(ruta_destino, nuevo_nombre))

                if os.path.exists(ruta_nueva):
                    print(f"⏭️ Saltado (ya existe): {ruta_nueva}")
                    continue

                try:
                    img = Image.open(ruta_archivo)
                    img = ImageOps.exif_transpose(img).convert("RGB")
                    nuevo_nombre = f"{nombre}_opt.jpeg"
                    ruta_nueva = os.path.join(ruta_destino, nuevo_nombre)

                    img.save(ruta_nueva, "JPEG", optimize=True, quality=calidad_img)
                    print(f"🖼️ {ruta_archivo} → {ruta_nueva}")
                except Exception as e:
                    print(f"❌ Error con imagen {ruta_archivo}: {e}")

            # Procesar videos
            elif ext in extensiones_vid:
                nuevo_nombre = f"{nombre}_opt.mp4"
                ruta_nueva = os.path.normpath(os.path.join(ruta_destino, nuevo_nombre))

                if os.path.exists(ruta_nueva):
                    print(f"⏭️ Saltado (ya existe): {ruta_nueva}")
                    continue

                try:
                    (
                        ffmpeg
                        .input(ruta_archivo)
                        .output(ruta_nueva, vcodec=codec_video, crf=crf, preset=preset, acodec="aac")
                        .run(overwrite_output=True, quiet=True)
                    )
                    print(f"🎬 {ruta_archivo} → {ruta_nueva}")
                except Exception as e:
                    print(f"❌ Error con video {ruta_archivo}: {e}")

    print(f"\n🚀 Optimización completada. Carpeta generada: {carpeta_opt}")


if __name__ == "__main__":
    Tk().withdraw()
    carpeta_seleccionada = filedialog.askdirectory(title="Selecciona la carpeta con imágenes y/o videos")

    if carpeta_seleccionada:
        start_time = time.time()
        renombrarArchivos(carpeta_seleccionada)
        print("\nSe comenzará a realizar la optimización de archivos: ")
        optimizar_archivos(carpeta_seleccionada, calidad_img=80, codec_video="libx265", crf=28, preset="medium")

        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print("\n✅ Optimización de archivos completada")
        print(f"Tiempo transcurrido: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    else:
        print("No seleccionaste ninguna carpeta.")
