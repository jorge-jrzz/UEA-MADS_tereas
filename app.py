from random import randint

from flask import Flask, render_template, request, redirect, url_for, flash

from config import DevelopmentConfig
from models import db, Producto, Departamento, ProductoDepartamento, Precio, init_db

app = Flask(__name__)
app.config.from_object(DevelopmentConfig())

# Inicializar la base de datos
init_db(app)

# ----- RUTAS PARA LAS PÁGINAS PRINCIPALES -----
@app.route('/')
def index():
    return render_template('index.html')

# ----- RUTAS PARA PRODUCTOS -----
@app.route('/productos/alta', methods=['GET', 'POST'])
def alta_producto():
    if request.method == 'POST':
        codigo = randint(1000, 9999)
        nombre = request.form['nombre']
        proveedor = request.form.get('proveedor')

        # Verificar si el producto ya existe
        producto_existente = Producto.query.filter_by(codigo=codigo).first()
        if producto_existente:
            flash('El código de producto ya existe', 'danger')
            return render_template('productos/alta_producto.html')

        # Crear nuevo producto
        nuevo_producto = Producto(
            codigo=codigo,
            nombre=nombre,
            proveedor=proveedor
        )

        try:
            db.session.add(nuevo_producto)
            db.session.commit()
            flash('Producto agregado correctamente', 'success')
            return redirect(url_for('consultar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar producto: {str(e)}', 'danger')

    return render_template('productos/alta_producto.html')

@app.route('/productos/baja', methods=['GET', 'POST'])
def baja_producto():
    if request.method == 'POST':
        producto_id = request.form.get('producto_id')
        producto = Producto.query.get_or_404(producto_id)

        try:
            db.session.delete(producto)
            flash(f"Producto {producto.nombre} borrado correctamente.", "danger")
            db.session.commit()
            return redirect(url_for('consultar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar el producto: {str(e)}', 'danger')

    # Obtener todos los productos sin filtrar por estado activo
    productos = Producto.query.all()
    return render_template('productos/baja_producto.html', productos=productos)

@app.route('/productos/renovar', methods=['GET', 'POST'])
def renovar_producto():
    if request.method == 'GET':
        producto_id = request.args.get('producto_id')
        producto = Producto.query.get_or_404(producto_id)
        producto.change_state()

        try:
            db.session.commit()
            flash('Producto renovado correctamente', 'success')
            return redirect(url_for('consultar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al renovar el producto: {str(e)}', 'danger')

    return redirect(url_for('consultar_productos'))

@app.route('/productos/consultar')
def consultar_productos():
    productos = Producto.query.all()
    asignaciones = ProductoDepartamento.query.all()
    return render_template('productos/consultar_productos.html', productos=productos, asignaciones=asignaciones)

# ----- RUTAS PARA DEPARTAMENTOS -----

@app.route('/departamentos/alta', methods=['GET', 'POST'])
def alta_departamento():
    if request.method == 'POST':
        codigo = request.form['codigo']
        nombre = request.form['nombre']
        responsable = request.form['responsable']

        # Verificar si el departamento ya existe
        departamento_existente = Departamento.query.filter_by(codigo=codigo).first()
        if departamento_existente:
            flash('El código de departamento ya existe', 'danger')
            return render_template('departamentos/alta_departamento.html')

        # Crear nuevo departamento
        nuevo_departamento = Departamento(
            codigo=codigo,
            nombre=nombre,
            responsable=responsable
        )

        try:
            db.session.add(nuevo_departamento)
            db.session.commit()
            flash('Departamento agregado correctamente', 'success')
            return redirect(url_for('consultar_departamentos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al agregar departamento: {str(e)}', 'danger')

    return render_template('departamentos/alta_departamento.html')

@app.route('/departamentos/baja', methods=['GET', 'POST'])
def baja_departamento():
    if request.method == 'POST':
        departamento_id = request.form.get('departamento_id')
        departamento = Departamento.query.get_or_404(departamento_id)

        try:
            db.session.delete(departamento)
            flash(f"Departamento {departamento.nombre} borrado correctamente.", "danger")
            db.session.commit()
            return redirect(url_for('consultar_departamentos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al eliminar el departamento: {str(e)}', 'danger')

    departamentos = Departamento.query.all()
    return render_template('departamentos/baja_departamento.html', departamentos=departamentos)

@app.route('/departamentos/renovar', methods=['GET', 'POST'])
def renovar_departamento():
    if request.method == 'GET':
        departamento_id = request.args.get('departamento_id')
        departamento = Departamento.query.get_or_404(departamento_id)
        departamento.change_state()

        try:
            db.session.commit()
            flash('Departamento renovado correctamente', 'success')
            return redirect(url_for('consultar_departamentos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al renovar el producto: {str(e)}', 'danger')

    return redirect(url_for('consultar_departamentos'))

@app.route('/departamentos/consultar')
def consultar_departamentos():
    departamentos = Departamento.query.all()
    return render_template('departamentos/consultar_departamentos.html', departamentos=departamentos)

# ----- RUTAS PARA ASIGNACIONES DE PRODUCTOS A DEPARTAMENTOS -----

@app.route('/asignaciones/alta', methods=['GET', 'POST'])
def alta_producto_depto():
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        departamento_id = request.form['departamento_id']

        # Verificar si la asignación ya existe
        asignacion_existente = ProductoDepartamento.query.filter_by(
            producto_id=producto_id,
        ).first()

        if asignacion_existente:
            flash('El producto ya está asignado', 'warning')
            return redirect(url_for('alta_producto_depto'))

        # Crear nueva asignación
        nueva_asignacion = ProductoDepartamento(
            producto_id=producto_id,
            departamento_id=departamento_id
        )

        try:
            db.session.add(nueva_asignacion)
            db.session.commit()
            flash('Producto asignado al departamento correctamente', 'success')
            return redirect(url_for('consultar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al asignar producto: {str(e)}', 'danger')

    productos = Producto.query.filter_by(activo=True).all()
    departamentos = Departamento.query.filter_by(activo=True).all()
    return render_template('asignaciones/alta_producto_depto.html',
                          productos=productos, departamentos=departamentos)

@app.route('/asignaciones/baja', methods=['GET', 'POST'])
def baja_producto_depto():
    if request.method == 'POST':
        asignacion_id = request.form['asignacion_id']
        asignacion = ProductoDepartamento.query.get_or_404(asignacion_id)

        try:
            db.session.delete(asignacion)
            flash('Producto retirado del departamento correctamente', 'success')
            db.session.commit()
            return redirect(url_for('consultar_productos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al retirar producto del departamento: {str(e)}', 'danger')

    # Obtener todas las asignaciones activas
    asignaciones = ProductoDepartamento.query.all()
    return render_template('asignaciones/baja_producto_depto.html', asignaciones=asignaciones)

# ----- RUTAS PARA PRECIOS -----

@app.route('/precios/consultar')
def consultar_precios_productos_depto():
    departamentos = Departamento.query.filter_by(activo=True).all()
    departamento_id = request.args.get('departamento_id', type=int)

    productos_con_precios = []

    if departamento_id:
        # Obtener productos del departamento seleccionado
        asignaciones = ProductoDepartamento.query.filter_by(
            departamento_id=departamento_id,
        ).all()

        for asignacion in asignaciones:
            # Obtener el precio más reciente para cada producto
            precio = Precio.query.filter_by(
                producto_id=asignacion.producto_id,
            ).order_by(Precio.fecha_asignacion.desc()).first()

            productos_con_precios.append({
                'producto': asignacion.producto,
                'departamento': Departamento.query.get(asignacion.departamento_id),
                'precio': precio.valor if precio else 'No asignado'
            })

    return render_template('precios/consultar_precios.html',
                          departamentos=departamentos,
                          departamento_actual=departamento_id,
                          productos=productos_con_precios)

@app.route('/precios/asignar', methods=['GET', 'POST'])
def asignar_precio_producto():
    if request.method == 'POST':
        producto_id = request.form['producto_id']
        valor = float(request.form['valor'])

        # Crear nuevo precio
        nuevo_precio = Precio(
            producto_id=producto_id,
            valor=valor
        )

        try:
            db.session.add(nuevo_precio)
            db.session.commit()
            flash('Precio asignado correctamente', 'success')
            return redirect(url_for('consultar_precios_productos_depto'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al asignar precio: {str(e)}', 'danger')

    productos = Producto.query.filter_by(activo=True).all()
    asignaciones = ProductoDepartamento.query.all()
    return render_template('precios/asignar_precio.html', productos=productos)

# Iniciar la aplicación
if __name__ == '__main__':
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
    )
