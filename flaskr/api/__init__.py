from flask import Flask
import os

environment_vars = os.environ

def create_app(config_name):
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = environment_vars['CONV_SQLALCHEMY_DATABASE_URI']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY']='frase-secreta'
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['PROCESSED_FOLDER'] = environment_vars['CONV_PROCESSED_FOLDER']
    app.config['UPLOAD_FOLDER'] = environment_vars['CONV_UPLOAD_FOLDER']
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    return app
