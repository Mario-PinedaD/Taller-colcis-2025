import os
import time
from PIL import Image, ImageOps
import ffmpeg
from tkinter import Tk, filedialog
from concurrent.futures import ThreadPoolExecutor
from renombrarRegex import renombrarArchivos

"""
Optimiza imágenes y videos en una carpeta (y subcarpetas) de forma recursiva
usando hilos de trabajo en paralelo. Los hilos son, como mínimo,
la mitad de los hilos que soporta el procesador.
"""

def convertir_a_resolve(ruta_entrada, ruta_salida):
    """
    Convierte un video a un formato ampliamente compatible con DaVinci Resolve:
    H.264 + yuv420p + AAC.
    """
    (
        ffmpeg
        .input(ruta_entrada)
        .output(
            ruta_salida,
            vcodec="libx264",
            pix_fmt="yuv420p",
            acodec="aac",
            movflags="+faststart"
        )
        .run(overwrite_output=True, quiet=True)
    )
    print(f"🎯 Convertido a Resolve: {ruta_entrada} → {ruta_salida}")


def procesar_archivo(ruta_archivo, ruta_destino,
                     calidad_img, codec_video, crf, preset):
    """
    Procesa un solo archivo (imagen o video).
    """
    nombre, ext = os.path.splitext(os.path.basename(ruta_archivo))
    ext = ext.lower()
    extensiones_img = (".jpg", ".png")
    extensiones_vid = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm")

    try:
        # ---- Imágenes ----
        if ext in extensiones_img:
            ruta_nueva = os.path.join(ruta_destino, f"{nombre}_opt.jpeg")
            if os.path.exists(ruta_nueva):
                print(f"⏭️ Saltado (ya existe): {ruta_nueva}")
                return
            img = Image.open(ruta_archivo)
            img = ImageOps.exif_transpose(img).convert("RGB")
            img.save(ruta_nueva, "JPEG", optimize=True, quality=calidad_img)
            print(f"🖼️ {ruta_archivo} → {ruta_nueva}")

        # ---- Videos ----
        elif ext in extensiones_vid:
            ruta_opt = os.path.join(ruta_destino, f"{nombre}_opt.mp4")
            if not os.path.exists(ruta_opt):
                (
                    ffmpeg
                    .input(ruta_archivo)
                    .output(ruta_opt,
                            vcodec=codec_video,
                            crf=crf,
                            preset=preset,
                            acodec="aac")
                    .run(overwrite_output=True, quiet=True)
                )
                print(f"🎬 {ruta_archivo} → {ruta_opt}")
            else:
                print(f"⏭️ Saltado (ya existe): {ruta_opt}")

            # Convertir a formato DaVinci
            ruta_resolve = os.path.join(ruta_destino, f"{nombre}_opt_R.mp4")
            if not os.path.exists(ruta_resolve):
                convertir_a_resolve(ruta_opt, ruta_resolve)
            else:
                print(f"⏭️ Saltado (ya existe): {ruta_resolve}")

    except Exception as e:
        print(f"❌ Error con {ruta_archivo}: {e}")


def optimizar_archivos_parallel(carpeta, calidad_img=80,
                                codec_video="libx265", crf=28, preset="medium"):
    """
    Recorre la carpeta, prepara tareas y las ejecuta en paralelo.
    """
    carpeta_opt = carpeta.rstrip(os.sep) + "-optimizados"
    os.makedirs(carpeta_opt, exist_ok=True)

    tareas = []
    for ruta_actual, _, archivos in os.walk(carpeta):
        ruta_relativa = os.path.relpath(ruta_actual, carpeta)
        ruta_destino = os.path.join(carpeta_opt, ruta_relativa)
        os.makedirs(ruta_destino, exist_ok=True)

        for archivo in archivos:
            tareas.append((
                os.path.join(ruta_actual, archivo),
                ruta_destino,
                calidad_img,
                codec_video,
                crf,
                preset
            ))

    num_threads = max(1, os.cpu_count() // 2)
    print(f"🔧 Usando {num_threads} hilos de trabajo…\n")

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        executor.map(lambda args: procesar_archivo(*args), tareas)

    print(f"\n🚀 Optimización completada. Carpeta generada: {carpeta_opt}")


if __name__ == "__main__":
    Tk().withdraw()
    carpeta_seleccionada = filedialog.askdirectory(
        title="Selecciona la carpeta con imágenes y/o videos"
    )

    if carpeta_seleccionada:
        start_time = time.time()
        renombrarArchivos(carpeta_seleccionada)

        print("\nSe comenzará a realizar la optimización de archivos: ")
        optimizar_archivos_parallel(
            carpeta_seleccionada,
            calidad_img=80,
            codec_video="libx265",
            crf=28,
            preset="medium"
        )

        elapsed_time = time.time() - start_time
        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        print("\n✅ Optimización de archivos completada")
        print(f"Tiempo transcurrido: {int(hours)}h {int(minutes)}m {seconds:.2f}s")
    else:
        print("No seleccionaste ninguna carpeta.")
