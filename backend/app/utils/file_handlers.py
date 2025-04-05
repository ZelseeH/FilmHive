import os
from werkzeug.utils import secure_filename
import uuid
from flask import current_app
import json

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}
UPLOAD_FOLDER = "static/uploads/users"


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# utils/file_handlers.py
def save_user_image(file, username, image_type, position=None):
    """
    Zapisuje zdjęcie użytkownika w odpowiednim folderze.

    Args:
        file: Obiekt pliku z request.files
        username: Nazwa użytkownika
        image_type: Typ zdjęcia ('profile_picture' lub 'background_image')
        position: Słownik z pozycją x, y dla zdjęcia w tle

    Returns:
        Słownik z ścieżką do pliku i pozycją
    """
    if not file or file.filename == "":
        return None

    if not allowed_file(file.filename):
        return None

    user_folder = os.path.join(current_app.root_path, UPLOAD_FOLDER, username)
    os.makedirs(user_folder, exist_ok=True)

    # Usuń stare pliki
    for existing_file in os.listdir(user_folder):
        if existing_file.startswith(image_type):
            try:
                os.remove(os.path.join(user_folder, existing_file))
            except Exception as e:
                print(f"Błąd podczas usuwania starego pliku: {e}")

    filename = secure_filename(file.filename)
    file_extension = filename.rsplit(".", 1)[1].lower() if "." in filename else "jpg"
    unique_id = uuid.uuid4().hex[:8]
    new_filename = f"{image_type}_{unique_id}.{file_extension}"

    file_path = os.path.join(user_folder, new_filename)
    file.save(file_path)

    # Zapisz pozycję do pliku JSON, jeśli podano
    if position and image_type == "background_image":
        position_file = os.path.join(
            user_folder, f"{image_type}_{unique_id}_position.json"
        )
        with open(position_file, "w") as f:
            json.dump(position, f)

    return f"uploads/users/{username}/{new_filename}"
