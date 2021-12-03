from flask_restful import Api
from api import create_app
from flask_jwt_extended import JWTManager
from api.vistas import VistaUsuarios, VistaLogIn, VistaTareasConversion, VistaDescargaArchivo, VistaSignup, VistaTareaConversion
from api.modelos import db, Usuario, TareaConversion, EstadoProcesoConversion, TareaConversionSchema
import datetime
import pytz
import logging
import os

environment_vars = os.environ

app = create_app('default')
app_context =app.app_context()
app_context.push()

db.init_app(app)
db.create_all()

api = Api(app)
api.add_resource(VistaUsuarios, '/api/usuarios')
api.add_resource(VistaSignup, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaTareasConversion, '/api/tasks')
api.add_resource(VistaTareaConversion, '/api/tasks/<int:id_task>')
api.add_resource(VistaDescargaArchivo, '/api/files/<string:filename>')

jwt = JWTManager(app)

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(environment_vars['CONV_SQLALCHEMY_ENGINE_LOG_LEVEL'])

app.logger.setLevel(environment_vars['CONV_APP_LOG_LEVEL'])

log = logging.getLogger('werkzeug')
log.setLevel(environment_vars['CONV_APP_LOG_LEVEL'])
