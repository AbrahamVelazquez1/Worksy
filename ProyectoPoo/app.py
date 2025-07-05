from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'mssql+pyodbc://localhost/Worksy?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=yes'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelos
class Municipio(db.Model):
    __tablename__ = 'municipio'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)

class Estado(db.Model):
    __tablename__ = 'estado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)

class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)

class Jornada(db.Model):
    __tablename__ = 'jornada'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)

class Area(db.Model):
    __tablename__ = 'area'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)

class Subarea(db.Model):
    __tablename__ = 'subarea'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String)
    idarea = db.Column(db.Integer, db.ForeignKey('area.id'))
    area = db.relationship('Area')

class Direccion(db.Model):
    __tablename__ = 'direccion'
    id = db.Column(db.Integer, primary_key=True)
    idmunicipio = db.Column(db.Integer, db.ForeignKey('municipio.id'))
    idestado = db.Column(db.Integer, db.ForeignKey('estado.id'))
    municipio = db.relationship('Municipio')
    estado = db.relationship('Estado')

class Vacante(db.Model):
    __tablename__ = 'vacante'
    id = db.Column(db.Integer, primary_key=True)
    idempresa = db.Column(db.Integer, db.ForeignKey('empresa.id'))
    iddireccion = db.Column(db.Integer, db.ForeignKey('direccion.id'))
    idjornada = db.Column(db.Integer, db.ForeignKey('jornada.id'))
    nombre = db.Column(db.String)
    salario = db.Column(db.Float)
    fechapublicacion = db.Column(db.String)
    descripcion = db.Column(db.String)
    requerimientos = db.Column(db.String)
    idarea = db.Column(db.Integer, db.ForeignKey('area.id'))
    idsubarea = db.Column(db.Integer, db.ForeignKey('subarea.id'))

    empresa = db.relationship('Empresa')
    direccion = db.relationship('Direccion')
    jornada = db.relationship('Jornada')
    area = db.relationship('Area')
    subarea = db.relationship('Subarea')

@app.route('/', methods=['GET'])
def index():
    # Filtros
    municipio = request.args.get('municipio', '')
    estado = request.args.get('estado', '')
    jornada = request.args.get('jornada', '')
    area = request.args.get('area', '')
    subarea = request.args.get('subarea', '')
    search = request.args.get('search', '')

    query = Vacante.query.join(Vacante.empresa).join(Vacante.direccion).join(Direccion.municipio).join(Direccion.estado).join(Vacante.jornada).join(Vacante.area).join(Vacante.subarea)

    # Aplicar filtros (asegúrate de comparar ids como enteros)
    if municipio:
        query = query.filter(Direccion.idmunicipio == int(municipio))
    if estado:
        query = query.filter(Direccion.idestado == int(estado))
    if jornada:
        query = query.filter(Vacante.idjornada == int(jornada))
    if area:
        query = query.filter(Vacante.idarea == int(area))
    if subarea:
        query = query.filter(Vacante.idsubarea == int(subarea))
    if search:
        search_like = f'%{search}%'
        query = query.filter(
            (Vacante.nombre.ilike(search_like)) |
            (Vacante.descripcion.ilike(search_like)) |
            (Vacante.requerimientos.ilike(search_like)) |
            (Empresa.nombre.ilike(search_like))
        )

    vacantes = query.all()
    # Seleccionar 8 aleatorias si hay más de 8
    if len(vacantes) > 8:
        vacantes = random.sample(vacantes, 8)

    # Para los selects dinámicos
    municipios = Municipio.query.all()
    estados = Estado.query.all()
    jornadas = Jornada.query.all()
    areas = Area.query.all()
    subareas = Subarea.query.all()

    return render_template(
        'index.html',
        ofertas=vacantes,
        municipios=municipios,
        estados=estados,
        jornadas=jornadas,
        areas=areas,
        subareas=subareas,
        filtros={
            'municipio': municipio,
            'estado': estado,
            'jornada': jornada,
            'area': area,
            'subarea': subarea,
            'search': search
        }
    )

if __name__ == '__main__':
    app.run(debug=True)