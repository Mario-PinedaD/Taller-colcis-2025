import os
from PIL import Image, ImageOps
import ffmpeg
import time
from tkinter import Tk, filedialog
from renombrarRegex import renombrarArchivos

"""
Asegúrate de que ffmpeg esté instalado en el sistema y agregado al PATH.
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


def optimizar_archivos(carpeta, calidad_img=80,
                       codec_video="libx265", crf=28, preset="medium"):
    """
    Optimiza imágenes y videos en una carpeta (y subcarpetas) de forma recursiva.
    - Imágenes: se comprimen en JPEG.
    - Videos: 1) se comprimen en H.265, 2) se convierten a formato DaVinci (H.264).
    Genera una nueva carpeta raíz con sufijo '-optimizados'.
    """
    carpeta_opt = carpeta.rstrip(os.sep) + "-optimizados"
    os.makedirs(carpeta_opt, exist_ok=True)

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

            # ---- Imágenes ----
            if ext in extensiones_img:
                nuevo_nombre = f"{nombre}_opt.jpeg"
                ruta_nueva = os.path.normpath(os.path.join(ruta_destino, nuevo_nombre))
                if os.path.exists(ruta_nueva):
                    print(f"⏭️ Saltado (ya existe): {ruta_nueva}")
                    continue
                try:
                    img = Image.open(ruta_archivo)
                    img = ImageOps.exif_transpose(img).convert("RGB")
                    img.save(ruta_nueva, "JPEG", optimize=True, quality=calidad_img)
                    print(f"🖼️ {ruta_archivo} → {ruta_nueva}")
                except Exception as e:
                    print(f"❌ Error con imagen {ruta_archivo}: {e}")

            # ---- Videos ----
            elif ext in extensiones_vid:
                # 1) Comprimir a H.265
                nombre_opt = f"{nombre}_opt.mp4"
                ruta_opt = os.path.normpath(os.path.join(ruta_destino, nombre_opt))
                if not os.path.exists(ruta_opt):
                    try:
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
                    except Exception as e:
                        print(f"❌ Error con video {ruta_archivo}: {e}")
                        continue
                else:
                    print(f"⏭️ Saltado (ya existe): {ruta_opt}")

                # 2) Convertir a formato compatible DaVinci
                nombre_resolve = f"{nombre}_opt_R.mp4"
                ruta_resolve = os.path.normpath(os.path.join(ruta_destino, nombre_resolve))
                if not os.path.exists(ruta_resolve):
                    try:
                        convertir_a_resolve(ruta_opt, ruta_resolve)
                    except Exception as e:
                        print(f"❌ Error al convertir a Resolve {ruta_opt}: {e}")
                else:
                    print(f"⏭️ Saltado (ya existe): {ruta_resolve}")

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
        optimizar_archivos(
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
