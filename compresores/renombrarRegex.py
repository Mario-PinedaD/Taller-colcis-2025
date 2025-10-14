import os
import re
from datetime import datetime
from PIL import Image, ExifTags
import piexif

def obtener_fecha_captura(ruta_archivo):
    try:
        # Para imágenes (JPEG, PNG, etc.)
        if ruta_archivo.lower().endswith(('.jpg', '.jpeg', '.png')):
            img = Image.open(ruta_archivo)
            exif_data = img._getexif() or {}
            
            # Buscar la fecha en los metadatos EXIF
            for tag, value in exif_data.items():
                tag_nombre = ExifTags.TAGS.get(tag, tag)
                if tag_nombre == 'DateTimeOriginal':
                    fecha_str = value
                    return datetime.strptime(fecha_str, "%Y:%m:%d %H:%M:%S")
        
        # Para videos (usando exiftool externo)
        elif ruta_archivo.lower().endswith(('.mp4', '.mov', '.avi')):
            import subprocess
            result = subprocess.run(
                ['exiftool', '-CreateDate', '-d', '%Y:%m:%d %H:%M:%S', '-s3', ruta_archivo],
                capture_output=True, text=True
            )
            if result.stdout.strip():
                return datetime.strptime(result.stdout.strip(), "%Y:%m:%d %H:%M:%S")
    
    except Exception as e:
        print(f"⚠️ No se pudo obtener la fecha de captura para {ruta_archivo}: {e}")
    
    # Si no hay metadatos, usar fecha de modificación como fallback
    timestamp_mod = os.path.getmtime(ruta_archivo)
    return datetime.fromtimestamp(timestamp_mod)

def renombrarArchivos(directorio):
    # Obtener la carpeta donde está ubicado este script
    patron = re.compile(r'^(IMG|MVI)_(\d+)\.(.+)$', re.IGNORECASE)
    
    print(f"🔍 Buscando archivos desde: {directorio}...")
    
    for raiz, _, archivos in os.walk(directorio):
        for archivo in archivos:
            coincidencia = patron.match(archivo)
            if coincidencia:
                prefijo, numero, extension = coincidencia.groups()
                ruta_completa = os.path.join(raiz, archivo)
                
                fecha_captura = obtener_fecha_captura(ruta_completa)
                fecha_str = fecha_captura.strftime("%Y%m%d")
                
                nuevo_nombre = f"{fecha_str}_{numero}.{extension}"
                nueva_ruta = os.path.join(raiz, nuevo_nombre)
                
                try:
                    os.rename(ruta_completa, nueva_ruta)
                    print(f"✅ Renombrado: {archivo} → {nuevo_nombre}")
                except Exception as e:
                    print(f"❌ Error al renombrar {archivo}: {e}")