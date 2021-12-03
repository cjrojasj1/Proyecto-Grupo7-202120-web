from flask_sqlalchemy import SQLAlchemy
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields
import enum
import datetime
import pytz


db = SQLAlchemy()

class EstadoProcesoConversion(enum.Enum):
   UPLOADED = 1
   PROCESSED = 2
   PROCESSING = 3
    
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(50), nullable=False)
    tareas_conversion = db.relationship('TareaConversion', cascade='all, delete, delete-orphan')
    __table_args__ = (db.UniqueConstraint('email', name='email_uk'),db.UniqueConstraint('username', name='username_uk'),)

class TareaConversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre_archivo = db.Column(db.String(100), nullable=False)
    extension_original = db.Column(db.String(5), nullable=False)
    extension_conversion = db.Column(db.String(5), nullable=False)
    estado_conversion = db.Column(db.Enum(EstadoProcesoConversion), nullable=False)
    fecha_registro = db.Column(db.DateTime(timezone=True), default=datetime.datetime.now(pytz.timezone('Etc/GMT+5')))
    fecha_procesamiento = db.Column(db.DateTime(timezone=True), nullable=True)
    usuario = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

class EnumADiccionario(fields.Field):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return {"llave": value.name, "valor": value.value}

class TareaConversionFullSchema(SQLAlchemyAutoSchema):
    estado_conversion = EnumADiccionario(attribute=("estado_conversion"))
    class Meta:
         model = TareaConversion
         include_relationships = True
         load_instance = True

class UsuarioSchema(SQLAlchemyAutoSchema):
    class Meta:
         model = Usuario
         include_relationships = False
         load_instance = True

class TareaConversionSchema(SQLAlchemyAutoSchema):
    estado_conversion = EnumADiccionario(attribute=("estado_conversion"))
    class Meta:
        fields = ("id", "nombre_archivo", "extension_original", "extension_conversion", "estado_conversion", "fecha_registro")
