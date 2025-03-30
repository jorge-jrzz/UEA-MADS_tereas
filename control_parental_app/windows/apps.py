import winreg
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional

from icons import IconHandler  


class AppManager:
    def __init__(self, output_json: Path = Path("apps_gg.json")) -> None:
        """
        Inicializa la clase y prepara el manejador de iconos.
        """
        self.output_json = output_json
        self.icon_handler = IconHandler()

    @staticmethod
    def is_interesting_app(app_info: Dict[str, str]) -> bool:
        """
        Determina si una aplicación es de interés.
        Filtra aplicaciones del sistema y de Microsoft.
        """
        name = app_info.get("name", "").strip().lower()
        publisher = app_info.get("publisher", "").strip().lower()
        install_location = app_info.get("install_location", "").strip().lower()

        if publisher in ("microsoft corporation", "microsoft"):
            return False

        # Filtrar por el nombre: si contiene puntos, se evalúa la primera parte
        name_parts = name.split(".")
        if len(name_parts) > 1:
            if name_parts[0].startswith("microsoft") or name_parts[0].startswith("windows"):
                return False

        install_location_parts = install_location.split("\\")
        if len(install_location_parts) > 3:
            if install_location_parts[2] == "systemapps":
                return False

        return True

    def get_installed_apps_from_registry(self, hive, flag) -> List[Dict[str, str]]:
        """
        Obtiene aplicaciones tradicionales del Registro de Windows.
        Se utiliza un context manager para asegurar el cierre de la clave.
        """
        apps = []
        try:
            reg = winreg.ConnectRegistry(None, hive)
            with winreg.OpenKey(reg, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall", 0, winreg.KEY_READ | flag) as key:
                count = winreg.QueryInfoKey(key)[0]
                for i in range(count):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            except FileNotFoundError:
                                continue  # Saltar si no tiene DisplayName

                            try:
                                publisher = winreg.QueryValueEx(subkey, "Publisher")[0]
                            except FileNotFoundError:
                                publisher = ""

                            try:
                                version = winreg.QueryValueEx(subkey, "DisplayVersion")[0]
                            except FileNotFoundError:
                                version = ""

                            try:
                                install_location = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                            except FileNotFoundError:
                                install_location = ""
                            
                            try:
                                icon = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                            except FileNotFoundError:
                                icon = ""

                            app_info = {
                                "name": display_name,
                                "publisher": publisher,
                                "version": version,
                                "install_location": install_location,
                                "icon": icon,
                                "source": "External"
                            }

                            if not AppManager.is_interesting_app(app_info):
                                continue

                            apps.append(app_info)
                    except EnvironmentError:
                        continue
            return apps
        except Exception as e:
            print(f"Error al acceder al Registro: {e}")
            return []

    def get_installed_apps_from_store(self) -> List[Dict[str, str]]:
        """
        Obtiene aplicaciones de la Microsoft Store usando PowerShell.
        Se gestiona el caso de recibir un único objeto JSON.
        """
        apps = []
        try:
            cmd = 'powershell -ExecutionPolicy Bypass -Command "Get-AppxPackage | ConvertTo-Json"'
            result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
            if result.returncode != 0:
                print(f"Error al ejecutar PowerShell: {result.stderr}")
                return apps

            try:
                apps_data = json.loads(result.stdout)
            except json.JSONDecodeError as e:
                print(f"Error al parsear JSON: {e}")
                return apps

            # Si se recibió un único objeto, se convierte a lista
            if isinstance(apps_data, dict):
                apps_data = [apps_data]

            for app in apps_data:
                app_info = {
                    "name": app.get("Name", ""),
                    "publisher": app.get("Publisher", ""),
                    "version": app.get("Version", ""),
                    "install_location": app.get("InstallLocation", ""),
                    "icon": "",
                    "source": "Microsoft Store"
                }

                if not AppManager.is_interesting_app(app_info):
                    continue

                apps.append(app_info)
            return apps
        except Exception as e:
            print(f"Error al obtener aplicaciones de la Store: {e}")
            return apps

    def add_icons_to_apps(self, apps: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Añade el icono a cada aplicación utilizando la clase IconHandler.
        Actualiza la clave 'icon' con la ruta absoluta del icono extraído.
        """
        for app in apps:
            icon_path = self.icon_handler.save_icon(app)
            app["icon"] = str(Path(icon_path).resolve()) if icon_path else None
        return apps
    



    def run(self) -> None:
        """
        Ejecuta el proceso completo:
         - Obtiene aplicaciones desde el Registro y la Microsoft Store.
         - Combina y ordena la lista.
         - Añade iconos a cada aplicación.
         - Guarda el resultado en un archivo JSON.
        """
        registry_apps = (
            self.get_installed_apps_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_64KEY) +
            self.get_installed_apps_from_registry(winreg.HKEY_LOCAL_MACHINE, winreg.KEY_WOW64_32KEY) +
            self.get_installed_apps_from_registry(winreg.HKEY_CURRENT_USER, 0)
        )
        store_apps = self.get_installed_apps_from_store()

        combined_apps = registry_apps + store_apps
        combined_apps.sort(key=lambda x: x["name"].lower())
        combined_apps = self.add_icons_to_apps(combined_apps)

        try:
            with open(self.output_json, "w", encoding="utf-8") as f:
                json.dump(combined_apps, f, indent=4, ensure_ascii=False)
            print(f"Archivo '{self.output_json}' generado correctamente.")
        except Exception as e:
            print(f"Error al guardar el archivo JSON: {e}")

class blockManager:
    @staticmethod
    def get_process_name(app: Dict[str, str]) -> str:
        """
        Extrae el nombre del ejecutable de la aplicación.
        Se utiliza la 'install_location' para determinar el archivo .exe que se debe cerrar.
        """        
        if app.get("install_location"):
            exe_path = Path(app["install_location"])
            if exe_path.is_file() and exe_path.suffix.lower() == ".exe":
                return exe_path.name
            elif exe_path.is_dir():
                exe_files = list(exe_path.glob("*.exe"))
                if exe_files:
                    return exe_files[0].name
        #como ultimo recurso, si el nombre de la aplicación parece ser un ejecutable, se utiliza
        if app['name'] and app['name'].lower().endswith(".exe"):
            return app['name']
        return None
    
    def close_applications (apps: List[Dict[str, str]]) -> None:
        for app in apps:
            process_name = blockManager.get_process_name(app)
            if process_name:
                try:
                    subprocess.run(["taskkill", "/IM", process_name, "/F"], capture_output=True, text=True, check=True)
                    print(f"Se cerró la aplicación: {app['name']} (Proceso: {process_name})")
                except subprocess.CalledProcessError as e:
                    print(f"No se pudo cerrar la aplicación: {app['name']} (Proceso: {process_name}). Error: {e.stderr}")
            else:
                print(f"No se pudo determinar el proceso para la aplicación: {app['name']}")
    
    #Implementar lo de la base de datos
    def save_blocked_apps(apps: List[Dict[str, str]]) -> None:
        print("Guardando las aplicaciones bloqueadas en la base de datos (stub).")
        # db.save(apps)
            


if __name__ == "__main__":
    app_manager = AppManager()
    app_manager.run()
