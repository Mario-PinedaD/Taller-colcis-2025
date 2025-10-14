import os
import ffmpeg
from tkinter import Tk, filedialog

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

def convertir_videos_en_carpeta(carpeta):
    """
    Recorre recursivamente una carpeta y convierte todos los videos encontrados.
    Los nuevos archivos se guardan en la misma ubicación con sufijo '_R'.
    """
    extensiones_vid = (".mp4", ".mov", ".avi", ".mkv", ".flv", ".wmv", ".webm")

    print(f"\n🔍 Buscando videos en: {carpeta}\n")

    for raiz, _, archivos in os.walk(carpeta):
        for archivo in archivos:
            nombre, ext = os.path.splitext(archivo)
            if ext.lower() in extensiones_vid:
                ruta_entrada = os.path.join(raiz, archivo)
                ruta_salida = os.path.join(raiz, f"{nombre}_R.mp4")

                if os.path.exists(ruta_salida):
                    print(f"⏭️ Saltado (ya existe): {ruta_salida}")
                    continue

                try:
                    convertir_a_resolve(ruta_entrada, ruta_salida)
                except Exception as e:
                    print(f"❌ Error al convertir {archivo}: {e}")

    print("\n✅ Conversión completa. Todos los videos compatibles con DaVinci Resolve están listos.")

if __name__ == "__main__":
    Tk().withdraw()
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta con tus videos")

    if carpeta:
        convertir_videos_en_carpeta(carpeta)
    else:
        print("❌ No seleccionaste ninguna carpeta.")
