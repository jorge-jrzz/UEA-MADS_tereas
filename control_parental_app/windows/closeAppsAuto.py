import json
from apps import blockManager


def closeAppsAuto():
    # 1. Cargamos las aplicaciones desde el JSON generado por apps.py
    try:
        with open("apps.json", "r", encoding="utf-8") as f:
            all_apps = json.load(f)
    except FileNotFoundError:
        print("No se encontró el archivo apps.json. Ejecuta primero apps.py para generarlo.")
        return

    # 2. Mostramos las aplicaciones enumeradas para que el usuario elija
    print("Lista de aplicaciones encontradas:\n")
    for i, app in enumerate(all_apps):
        print(f"{i+1}. {app['name']}  (Ruta: {app['install_location']})")

    # 3. Pedimos que el usuario seleccione una (o varias) por número
    seleccion = input("\nIngresa el número de la aplicación que deseas cerrar (o varios separados por comas): ")
    indices = [s.strip() for s in seleccion.split(",") if s.strip().isdigit()]

    if not indices:
        print("Selección inválida. Saliendo...")
        return

    # 4. Construimos la lista de apps elegidas
    apps_a_cerrar = []
    for idx_str in indices:
        idx = int(idx_str) - 1
        if 0 <= idx < len(all_apps):
            apps_a_cerrar.append(all_apps[idx])

    if not apps_a_cerrar:
        print("No se seleccionó ninguna aplicación válida.")
        return

    # 5. Llamamos a close_applications con la lista de apps elegidas
    print("\nCerrando aplicaciones...\n")
    print("Aplicaciones a cerrar:")
    print(apps_a_cerrar)
    blockManager.close_applications(apps_a_cerrar)


if __name__ == "__main__":
    closeAppsAuto()
