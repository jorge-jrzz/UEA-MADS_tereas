from datetime import datetime

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


# Inicialización de la base de datos (sin app)
db = SQLAlchemy()

# Modelos de la base de datos
class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    proveedor = db.Column(db.String(80))
    fecha_creacion = db.Column(db.DateTime, default=datetime.now())
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Producto {self.nombre}>'
    
    def change_state(self):
        if self.activo:
            self.activo = False
        else:
            self.activo = True

class Departamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    responsable = db.Column(db.String(100), nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<Departamento {self.nombre}>'

    def change_state(self):
        if self.activo:
            self.activo = False
        else:
            self.activo = True

class ProductoDepartamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    departamento_id = db.Column(db.Integer, db.ForeignKey('departamento.id'), nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    producto = db.relationship('Producto', backref=db.backref('departamentos', lazy=True))
    departamento = db.relationship('Departamento', backref=db.backref('productos', lazy=True))

    def __repr__(self):
        return f'<ProductoDepartamento {self.producto.nombre} en {self.departamento.nombre}>'

class Precio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)

    producto = db.relationship('Producto', backref=db.backref('precios', lazy=True))

    def __repr__(self):
        return f'<Precio {self.valor} para {self.producto.nombre}>'

def init_db(app: Flask):
    """Inicializa la base de datos con la aplicación."""
    db.init_app(app)

    # Verificar si debemos crear las tablas
    with app.app_context():
        db.create_all()
