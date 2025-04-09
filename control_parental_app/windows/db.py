import json
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker

# Configuración de SQLAlchemy
Base = declarative_base()

class App(Base):
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    publisher = Column(String)
    version = Column(String)
    install_location = Column(String)
    icon = Column(String)
    source = Column(String)

def import_apps_from_json(json_path: str, db_path: str = "applications.db"):
    # Leer JSON desde archivo
    with open(json_path, 'r', encoding="utf-8") as json_file:
        data_json = json.load(json_file)

    # Crear la base de datos SQLite
    engine = create_engine(f'sqlite:///{db_path}', echo=True)
    Base.metadata.create_all(engine)

    # Crear sesión
    Session = sessionmaker(bind=engine)
    session = Session()

    # Insertar los datos
    for app in data_json:
        new_app = App(
            name=app["name"],
            publisher=app["publisher"],
            version=app["version"],
            install_location=app["install_location"],
            icon=app["icon"],
            source=app["source"]
        )
        session.add(new_app)

    # Guardar y cerrar sesión
    session.commit()
    session.close()

    print(f"✅ Datos insertados correctamente en '{db_path}'")

# Ejemplo de uso
if __name__ == "__main__":
    import_apps_from_json("apps.json")
