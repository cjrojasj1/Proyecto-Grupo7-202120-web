from celery import Celery
from flask import  request, jsonify, send_file, current_app, send_from_directory
from flask_restful import Resource
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity
from ..modelos import db, Usuario, UsuarioSchema, TareaConversionSchema, TareaConversionSchema, TareaConversion, EstadoProcesoConversion, TareaConversionFullSchema
from werkzeug.utils import secure_filename
from os import remove
import os
import io
import datetime
import pytz
import flask

usuario_schema = UsuarioSchema()
tarea_conversion_schema = TareaConversionSchema()
tarea_conversion_full_schema = TareaConversionFullSchema()

environment_vars = os.environ

allowed_exts = environment_vars['CONV_ALLOWED_EXTENSIONS'].split(',')

## Broker de mensajeria y worker
celery = Celery(__name__, broker=environment_vars['CONV_BROKER'])

@celery.task(name='registrar_tarea')
def registrar_tarea(*args):
    pass

class VistaUsuarios(Resource):
    
    def get(self):
        return [usuario_schema.dump(usuario) for usuario in Usuario.query.all()]

class VistaSignup(Resource):

    def post(self):
        password_one = request.json["password1"]
        password_two = request.json["password2"]
        if password_one == None or password_two == None or password_one != password_two:
            resp = jsonify({'mensaje' : 'Las contraseñas suministradas no coinciden'})
            resp.status_code = 400
            return resp
        nuevo_usuario = Usuario(username=request.json["username"], email=request.json["email"], contrasena=password_one)
        db.session.add(nuevo_usuario)
        db.session.commit()
        return usuario_schema.dump(nuevo_usuario)

class VistaLogIn(Resource):
    
    def post(self):
        usuario = Usuario.query.filter(Usuario.username == request.json["username"], Usuario.contrasena == request.json["password"]).first()
        if usuario is None:
            return "Username y contraseña ingresados son invalidos.", 400
        else:
            token_de_acceso = create_access_token(identity = usuario.id, expires_delta= False)
            return {"mensaje":"Inicio de sesión exitoso", "token": token_de_acceso} 

class VistaTareasConversion(Resource):
    
    @jwt_required()
    def get(self):
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get_or_404(id_usuario)
        return [tarea_conversion_schema.dump(tarea) for tarea in usuario.tareas_conversion]

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_exts
        
    @jwt_required()
    def post(self):
        id_usuario = get_jwt_identity()
        usuario = Usuario.query.get_or_404(id_usuario)
        filename = request.json["fileName"]
        new_format = request.json["newFormat"]

        if not self.allowed_file(filename) or new_format not in allowed_exts:
            resp = jsonify({'mensaje' : 'Los tipos de archivos permitidos son: {}'.format(environment_vars['CONV_ALLOWED_EXTENSIONS'])})
            resp.status_code = 400
            return resp
        
        try:
            with open(os.path.join(environment_vars['CONV_UPLOAD_FOLDER'], filename),'rb') as ifile:
                with open(os.path.join(environment_vars['CONV_PROCESSED_FOLDER'], filename), 'wb') as ofile:
                    data = ifile.read(1024*1024)
                    while data:
                        ofile.write(data)
                        data = ifile.read(1024*1024)

        except OSError as e:
            resp = jsonify({'mensaje' : 'El archivo no existe'})
            resp.status_code = 400
            return resp

        nueva_tarea_procesamiento = TareaConversion(nombre_archivo=filename, 
                                                    extension_original=filename.rsplit('.', 1)[1].lower(), 
                                                    extension_conversion=new_format, 
                                                    estado_conversion=EstadoProcesoConversion.UPLOADED, 
                                                    fecha_registro=datetime.datetime.now(pytz.timezone('Etc/GMT+5')), 
                                                    usuario=usuario.id)
           
        db.session.add(nueva_tarea_procesamiento)
        db.session.commit()
        
        args = [nueva_tarea_procesamiento.id]
        registrar_tarea.apply_async(args=args, queue=environment_vars['CONV_QUEUE'])

        resp = jsonify({"mensaje":"Se crea tarea de conversión exitosamente", "id_task": nueva_tarea_procesamiento.id})
        resp.status_code = 201
        return resp


class VistaTareaConversion(Resource):

    @jwt_required()    
    def get(self, id_task):
        id_usuario = get_jwt_identity()
        tarea = TareaConversion.query.get_or_404(id_task)
        if tarea.usuario != id_usuario:
            resp = jsonify({'mensaje' : 'La tarea no pertenece al usuario'})
            resp.status_code = 401
            return resp
        return tarea_conversion_schema.dump(tarea)

    @jwt_required()
    def put(self, id_task):
        id_usuario = get_jwt_identity()
        tarea = TareaConversion.query.get_or_404(id_task)
        if tarea.usuario != id_usuario:
            resp = jsonify({'mensaje' : 'La tarea no pertenece al usuario'})
            resp.status_code = 401
            return resp
        if tarea.estado_conversion == EstadoProcesoConversion.PROCESSED:
            #Borrar archivos
            try:
                filename = tarea.nombre_archivo.rsplit('.', 1)[0] + '.' +tarea.extension_conversion
                print(filename)
                remove(os.path.join(current_app.config['PROCESSED_FOLDER'], filename))
            except OSError as e:
                print(e)

        tarea.extension_conversion = request.json.get("newFormat",tarea.extension_conversion)
        tarea.estado_conversion = EstadoProcesoConversion.UPLOADED
        db.session.commit()
         

        return tarea_conversion_schema.dump(tarea)
    
    @jwt_required()
    def delete(self, id_task):
        id_usuario = get_jwt_identity()
        tarea = TareaConversion.query.get_or_404(id_task)
        if tarea.usuario != id_usuario:
            resp = jsonify({'mensaje' : 'La tarea no pertenece al usuario'})
            resp.status_code = 401
            return resp
        db.session.delete(tarea)
        db.session.commit()
        return '',204

    
class VistaDescargaArchivo(Resource):

    @jwt_required()
    def get(self, filename):
        return send_from_directory(current_app.config['PROCESSED_FOLDER'], filename, as_attachment=True)
