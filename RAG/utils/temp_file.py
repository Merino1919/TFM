import os
import mimetypes
import tempfile

def write_temp_file(uploaded_file):
    """
    Guarda uploaded_file (streamlit UploadedFile o similar) a un archivo temporal y devuelve la ruta.
    El archivo NO se borra aquí: el llamador debe eliminarlo tras usarlo.
    """
    suffix = ""
    name = getattr(uploaded_file, "name", None)
    if name:
        base_nombre, extension = os.path.splitext(name)
        suffix = extension
    else:
        # intentar inferir MIME
        mime = getattr(uploaded_file, "type", None)
        if mime:
            ext = mimetypes.guess_extension(mime.split(";")[0])
            suffix = ext or ""

    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        # Obtenemos los bytes
        data_bytes = uploaded_file.getvalue()
        # Los escribimos en el archivo temporal
        tf.write(data_bytes)
        tf.flush()
        return tf.name
    finally:
        tf.close()