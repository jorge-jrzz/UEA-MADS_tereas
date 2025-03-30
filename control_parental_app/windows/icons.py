import shutil
from pathlib import Path
from mimetypes import guess_type
from typing import Dict, List, Optional

from PIL import Image
from icoextract import IconExtractor, IconExtractorError


class IconHandler:
    def __init__(self, icons_directory: Path = Path("icons")) -> None:
        """
        Inicializa la clase y crea el directorio de iconos si no existe.
        """
        self.icons_path = icons_directory
        self.icons_path.mkdir(exist_ok=True)

    def is_icon_large_enough(self, icon_path: Path, min_width: int = 64, min_height: int = 64) -> bool:
        """
        Verifica si el icono en 'icon_path' contiene al menos una imagen (frame)
        con dimensiones mayores o iguales a min_width y min_height.
        """
        try:
            with Image.open(icon_path) as img:
                # Algunos archivos .ico contienen múltiples imágenes (frames)
                for frame in range(getattr(img, "n_frames", 1)):
                    if hasattr(img, "n_frames"):
                        img.seek(frame)
                    width, height = img.size
                    if width >= min_width and height >= min_height:
                        return True
            return False
        except Exception as e:
            print(f"Error al abrir el icono {icon_path}: {e}")
            return False
        
    def extract_icon_from_registry(self, icon_display: str) -> Optional[str]:
        """
        Extrae el icono a partir del valor 'DisplayIcon' obtenido del registro.
        Se espera que icon_display tenga el formato "ruta,índice".
        """
        icon_path = Path(icon_display.split(",")[0].strip())
        mime_type, _ = guess_type(str(icon_path))
        
        new_path = None  # <-- Inicializamos
        
        if mime_type and mime_type.startswith("image"):
            new_path = shutil.copy(icon_path, self.icons_path)
        elif mime_type and mime_type.startswith("application"):
            new_path = self.extract_icon_from_exe(icon_path)
        
        if new_path:
            return str(new_path)
        else:
            
            print(f"No se pudo extraer icono de: {icon_path}")
            return None
    
    def search_icon_file_in_dir(self, path: Path) -> Optional[Path]:
        """
        Busca de forma recursiva un archivo .ico dentro del directorio dado.
        """
        files_ico = list(path.rglob("*.ico"))
        return files_ico[0] if files_ico else None

    def list_exe_files_in_dir(self, path: Path) -> List[Path]:
        """
        Lista de forma recursiva todos los archivos .exe dentro del directorio dado.
        """
        return list(path.rglob("*.exe"))

    def extract_icon_from_install_location(self, install_path: str) -> str:
        """
        Intenta extraer el icono desde la ruta de instalación.
        Primero busca un archivo .ico; si no lo encuentra, recorre los ejecutables para extraer uno.
        """
        install_location_path = Path(install_path)
        icon_file = self.search_icon_file_in_dir(install_location_path)
        if icon_file and self.is_icon_large_enough(icon_file):
            new_path = shutil.copy(icon_file, self.icons_path)
            return new_path
        else:
            exe_files = self.list_exe_files_in_dir(install_location_path)
            if exe_files:
                for exe in exe_files:
                    new_path = self.extract_icon_from_exe(exe)
                    if new_path:
                        return str(new_path)

    def extract_icon_from_exe(self, exe_path: Path) -> Optional[Path]:
        """
        Extrae el icono desde un archivo ejecutable usando IconExtractor.
        Guarda el icono en el directorio de iconos y retorna la ruta del archivo.
        """
        try:
            if not exe_path.is_file():
                print(f"No existe el archivo: {exe_path}")
                return None
                
            extractor = IconExtractor(str(exe_path))
            new_icon_path = self.icons_path / f"{exe_path.stem}.ico"
            extractor.export_icon(str(new_icon_path), num=0)
            return new_icon_path
        except (IconExtractorError, FileNotFoundError):
            print(f"No se pudo extraer icono de: {exe_path}")
            return None


    def save_icon(self, app_data: Dict[str, str]) -> Optional[str]:
        """
        A partir de un diccionario con los datos de la aplicación (que incluya la clave 'icon'),
        procede a extraer el icono.
        """
        icon_data = app_data.get("icon")
        install_location = app_data.get("install_location")
        if icon_data and icon_data != "":
            new_path = self.extract_icon_from_registry(icon_data)
            return new_path
        elif install_location and install_location != "":
            new_path = self.extract_icon_from_install_location(install_location)
            return new_path
        else:
            print(f"No se pudo extraer icono para: {app_data['name']}")
            return None

# Ejemplo de uso:
if __name__ == "__main__":
    # Inicializa el gestor de iconos
    icon_handler = IconHandler()
    
    # Supongamos que tenemos datos de una aplicación en un diccionario
    app_info = {
        "name": "AppleInc.iCloud",
        "publisher": "CN=5BD5593D-A41B-4F89-884E-B4F3E0FBAA75",
        "version": "15.3.146.0",
        "install_location": "C:\\Program Files\\WindowsApps\\AppleInc.iCloud_15.3.146.0_x64__nzyj5cx40ttqa",
        "icon": "",
        "source": "Microsoft Store"
    }
    
    # Extrae y guarda el icono de la aplicación
    icon_handler.save_icon(app_info)
