import uuid
from src.database.supabase_client import supabase

def format_date(date):
    return date.strftime("%Y-%m-%d")

def upload_profile_picture(file_bytes, file_name, folder="general"):
    """
    Sube una foto al bucket 'perfiles' en Supabase Storage.
    Genera un nombre único para evitar colisiones.
    Retorna la URL pública de la imagen.
    """
    ext = file_name.split(".")[-1]
    unique_name = f"{folder}/{uuid.uuid4()}.{ext}"
    
    # Subir el archivo al bucket "perfiles"
    res = supabase.storage.from_("perfiles").upload(
        path=unique_name,
        file=file_bytes,
        file_options={"content-type": f"image/{ext}"}
    )
    
    # Obtener la URL pública
    public_url = supabase.storage.from_("perfiles").get_public_url(unique_name)
    return public_url
