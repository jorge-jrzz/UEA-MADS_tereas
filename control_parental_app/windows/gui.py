import flet as ft
import json
from pathlib import Path
import os
from apps import blockManager


class AppManager:
    def __init__(self):
        self.apps = []
        self.blacklist = set()
        self.default_icon = os.path.join(os.path.dirname(__file__), "df_icon.ico")
        self.load_blacklist()
    
    def load_apps_from_json(self, json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                self.apps = json.load(f)
            return True, "Aplicaciones cargadas correctamente"
        except Exception as e:
            return False, f"Error al cargar aplicaciones: {str(e)}"
    
    def load_blacklist(self):
        try:
            if Path("blacklist.json").exists():
                with open("blacklist.json", 'r') as f:
                    self.blacklist = set(json.load(f))
        except Exception as e:
            print(f"Error al cargar lista negra: {e}")
    
    def save_blacklist(self):
        try:
            with open("blacklist.json", 'w') as f:
                json.dump(list(self.blacklist), f)
        except Exception as e:
            print(f"Error al guardar lista negra: {e}")
    
    def toggle_blacklist(self, app_name):
        if app_name in self.blacklist:
            self.blacklist.remove(app_name)
            return False, f"{app_name} removido de la lista negra"
        else:
            self.blacklist.add(app_name)
            return True, f"{app_name} añadido a la lista negra"
    
    def get_app_icon(self, icon_path):
        if not icon_path or not Path(icon_path).exists():
            return self.default_icon if Path(self.default_icon).exists() else None
        return icon_path

def main(page: ft.Page):
    # Configuración de la página
    page.title = "Control Parental de Aplicaciones"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 20
    page.window_width = 1000
    page.window_height = 700
    page.window_resizable = True
    page.scroll = ft.ScrollMode.AUTO  # Habilitar scroll en toda la página
    
    app_manager = AppManager()
    
    # Variables de estado
    current_view = ft.Ref[ft.Column]()
    apps_list_view = ft.Ref[ft.ListView]()  # Cambiado a ListView para mejor scroll
    blacklist_view = ft.Ref[ft.ListView]()
    
    # Componentes de la UI
    def build_home_view():
        return ft.Column(
            controls=[
                ft.Image(src="https://cdn-icons-png.flaticon.com/512/3063/3063175.png", 
                        width=150, height=150),
                ft.Text("Control Parental de Aplicaciones", 
                       size=28, weight=ft.FontWeight.BOLD),
                ft.Text("Administra las aplicaciones instaladas en el sistema", 
                       size=16, color=ft.Colors.GREY_600),
                ft.Divider(height=40, color=ft.Colors.TRANSPARENT),
                ft.ElevatedButton(
                    "Escanear sistema",
                    icon=ft.Icons.SEARCH_OUTLINED,
                    on_click=lambda e: show_snackbar("Escaneo del sistema en progreso...", ft.Colors.BLUE),
                    style=ft.ButtonStyle(
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=300
                ),
                ft.ElevatedButton(
                    "Cargar aplicaciones desde archivo",
                    icon=ft.Icons.UPLOAD_FILE_OUTLINED,
                    on_click=lambda e: load_apps_from_file(),
                    style=ft.ButtonStyle(
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=300
                ),
                ft.ElevatedButton(
                    "Gestionar lista negra",
                    icon=ft.Icons.BLOCK_OUTLINED,
                    on_click=lambda e: show_blacklist_view(),
                    style=ft.ButtonStyle(
                        padding=20,
                        shape=ft.RoundedRectangleBorder(radius=10)
                    ),
                    width=300
                )
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        )
    
    def build_apps_list_view():
        apps_list_view.current = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True
        )
        
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Aplicaciones Instaladas", size=24, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=lambda e: show_home_view()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINED, color=ft.Colors.GREEN_400),
                                    ft.Text("Aplicación permitida", size=12)
                                ],
                                spacing=5
                            ),
                            padding=5,
                            border_radius=5,
                            bgcolor=ft.Colors.GREEN_50
                        ),
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.BLOCK_OUTLINED, color=ft.Colors.RED_400),
                                    ft.Text("Aplicación bloqueada", size=12)
                                ],
                                spacing=5
                            ),
                            padding=5,
                            border_radius=5,
                            bgcolor=ft.Colors.RED_50
                        )
                    ],
                    spacing=20
                ),
                ft.Divider(),
                apps_list_view.current
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def build_blacklist_view():
        blacklist_view.current = ft.ListView(
            expand=True,
            spacing=10,
            auto_scroll=True
        )
        
        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Gestión de Lista Negra", size=24, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=lambda e: show_home_view()
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                ft.Divider(),
                blacklist_view.current
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO
        )
    
    def show_snackbar(message, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(
            ft.Text(message),
            bgcolor=color
        )
        page.snack_bar.open = True
        page.update()
    
    def show_home_view():
        current_view.current.controls = [build_home_view()]
        page.update()
    
    def show_apps_list_view():
        current_view.current.controls = [build_apps_list_view()]
        update_apps_list_view()
        page.update()
    
    def show_blacklist_view():
        current_view.current.controls = [build_blacklist_view()]
        update_blacklist_view()
        page.update()
    
    def load_apps_from_file():
        success, message = app_manager.load_apps_from_json("apps.json")
        if success:
            show_apps_list_view()
            show_snackbar(message)
        else:
            show_snackbar(message, ft.Colors.RED)
        page.update()
    
    def update_apps_list_view():
        if not apps_list_view.current:
            return
            
        apps_list_view.current.controls.clear()
        
        if not app_manager.apps:
            apps_list_view.current.controls.append(
                ft.Text("No hay aplicaciones cargadas", italic=True)
            )
            return
        
        for app in app_manager.apps:
            icon_path = app_manager.get_app_icon(app.get('icon'))
            icon = ft.Icon(ft.Icons.APPS_OUTLINED) if not icon_path else ft.Image(
                src=icon_path, 
                width=32, 
                height=32,
                error_content=ft.Icon(ft.Icons.APPS_OUTLINED)
            )
            
            is_blacklisted = app['name'] in app_manager.blacklist
            
            apps_list_view.current.controls.append(
                ft.Card(
                    content=ft.Container(
                        content=ft.Row(
                            controls=[
                                icon,
                                ft.Column(
                                    controls=[
                                        ft.Text(app['name'], weight=ft.FontWeight.BOLD),
                                        ft.Text(f"Versión: {app['version']}", size=12),
                                        ft.Text(f"Editor: {app['publisher']}", size=12),
                                        ft.Text(f"Origen: {app['source']}", size=12),
                                    ],
                                    spacing=2,
                                    expand=True
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.CHECK_CIRCLE_OUTLINED if not is_blacklisted else ft.Icons.BLOCK_OUTLINED,
                                    icon_color=ft.Colors.GREEN_400 if not is_blacklisted else ft.Colors.RED_400,
                                    tooltip="Permitida (click para bloquear)" if not is_blacklisted else "Bloqueada (click para permitir)",
                                    on_click=lambda e, app_name=app['name']: toggle_app_blacklist(app_name, True if not is_blacklisted else False),
                                    #on_click=lambda e: toggle_app_blacklist(app_name, True)
                                )
                            ],
                            spacing=20,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        padding=10
                    ),
                    elevation=2
                )
            )
        page.update()
    
    def update_blacklist_view():
        if not blacklist_view.current:
            return
            
        blacklist_view.current.controls.clear()
        
        if not app_manager.blacklist:
            blacklist_view.current.controls.append(
                ft.Text("La lista negra está vacía", italic=True)
            )
            return
        
        for app_name in sorted(app_manager.blacklist):
            app = next((a for a in app_manager.apps if a['name'] == app_name), None)
            
            if app:
                icon_path = app_manager.get_app_icon(app.get('icon'))
                icon = ft.Icon(ft.Icons.APPS_OUTLINED) if not icon_path else ft.Image(
                    src=icon_path, 
                    width=32, 
                    height=32,
                    error_content=ft.Icon(ft.Icons.APPS_OUTLINED)
                )
                
                blacklist_view.current.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                controls=[
                                    icon,
                                    ft.Column(
                                        controls=[
                                            ft.Text(app['name'], weight=ft.FontWeight.BOLD),
                                            ft.Text(f"Versión: {app['version']}", size=12),
                                            ft.Text(f"Editor: {app['publisher']}", size=12),
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINED,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Quitar de lista negra",
                                        on_click=lambda e, app_name=app['name']: toggle_app_blacklist(app_name)
                                    )
                                ],
                                spacing=20,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=10
                        ),
                        elevation=2
                    )
                )
            else:
                blacklist_view.current.controls.append(
                    ft.Card(
                        content=ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Icon(ft.Icons.APPS_OUTLINED),
                                    ft.Column(
                                        controls=[
                                            ft.Text(app_name, weight=ft.FontWeight.BOLD),
                                            ft.Text("Información no disponible", size=12, color=ft.Colors.GREY_600),
                                        ],
                                        spacing=2,
                                        expand=True
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DELETE_OUTLINED,
                                        icon_color=ft.Colors.RED_400,
                                        tooltip="Quitar de lista negra",
                                        on_click=lambda e, app_name = app_name: toggle_app_blacklist(app_name)
                                    )
                                ],
                                spacing=20,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER
                            ),
                            padding=10
                        ),
                        elevation=2
                    )
                )
        page.update()
    
    def toggle_app_blacklist(app_name, blocked: bool = False):
        is_added, message = app_manager.toggle_blacklist(app_name)
        app_manager.save_blacklist()
        app = None
        for a in app_manager.apps:
            if a['name'] == app_name:
                app = a
                break
        
        # Actualizar ambas vistas para mantener consistencia
        if apps_list_view.current:
            update_apps_list_view()
        if blacklist_view.current:
            update_blacklist_view()

        if blocked and app:
            print(f"Cerrando aplicación: {app['name']}")
            print(app)
            blockManager.close_applications([app])
        
        show_snackbar(message, ft.Colors.GREEN_400 if not is_added else ft.Colors.RED_400)
        page.update()
    
    # Inicializar vista principal
    current_view.current = ft.Column(controls=[build_home_view()])
    page.add(current_view.current)

ft.app(target=main)
