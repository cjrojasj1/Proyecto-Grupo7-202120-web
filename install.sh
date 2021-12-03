sudo apt-get -y update
sudo apt-get -y install git
sudo apt-get -y install net-tools

cd ~
mkdir conversor_app
cd conversor_app
git clone --branch produccion-env-var-api https://github.com/MISW-4204-ComputacionEnNube/Proyecto-Grupo7-202120.git
cd Proyecto-Grupo7-202120/flaskr

cd ~
sudo apt-get -y install pip
sudo apt-get -y install postgresql postgresql-contrib libpq-dev
sudo apt-get -y install redis
sudo pip install -r requirements.txt

sudo pip install wheel
sudo apt-get -y install python3-venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
sudo ufw allow 5000
#gunicorn --bind 0.0.0.0:5000 wsgi:app
deactivate

sudo tee -a /etc/systemd/system/conversion_app.service > /dev/null <<EOT
[Unit]
Description=Gunicorn instance to serve APP
After=network.target

[Service]
User=estudiante
Group=estudiante
WorkingDirectory=/home/estudiante/conversor_app/Proyecto-Grupo7-202120/flaskr
Environment="PATH=/home/estudiante/conversor_app/Proyecto-Grupo7-202120/flaskr/venv/bin/"
ExecStart=/home/estudiante/conversor_app/Proyecto-Grupo7-202120/flaskr/venv/bin/gunicorn --workers 4 --bind unix:conversion_app.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
EOT

sudo usermod estudiante -a -G www-data
sudo systemctl start conversion_app
sudo systemctl enable conversion_app
sudo systemctl status conversion_app
sudo apt-get -y install nginx
sudo ufw app list
sudo ufw allow 'Nginx HTTP'
sudo systemctl status nginx

sudo tee -a /etc/nginx/sites-available/conversion_app > /dev/null <<EOT
[Unit]
server {
    listen 8080;
    server_name 172.23.66.142;

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/estudiante/conversor_app/Proyecto-Grupo7-202120/flaskr/conversion_app.sock;
    }
}
EOT

sudo ln -s /etc/nginx/sites-available/conversion_app /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
sudo ufw delete allow 5000
sudo ufw allow 'Nginx Full'
sudo systemctl status nginx

echo 'export CONV_CELERY_BROKER=redis://192.168.56.135:6379/0' >> ~/.bashrc
echo 'export CONV_UPLOAD_FOLDER=$HOME/conversion_files/uploads' >> ~/.bashrc
echo 'export CONV_PROCESSED_FOLDER=$HOME/conversion_files/processed' >> ~/.bashrc
echo 'export CONV_SQLALCHEMY_DATABASE_URI=postgresql://conversor:conversor1@192.168.56.133:5432/conversordb' >> ~/.bashrc
echo 'export CONV_REDIS_QUEUE=colatareas' >> ~/.bashrc
echo 'export CONV_ALLOWED_EXTENSIONS=mp3,acc,ogg,wav,wma' >> ~/.bashrc

echo 'export CONV_APP_HOME=$HOME/conversor_app/Proyecto-Grupo7-202120' >> ~/.bashrc
echo 'export CONV_APP_LOGS=$HOME/conversion_logs' >> ~/.bashrc

echo 'export CONV_SQLALCHEMY_ENGINE_LOG_LEVEL=INFO' >> ~/.bashrc
echo 'export CONV_APP_LOG_LEVEL=INFO' >> ~/.bashrc

echo 'export PATH=$PATH:$CONV_APP_HOME' >> ~/.bashrc

export CONV_CELERY_BROKER='redis://192.168.56.135:6379/0'
export CONV_UPLOAD_FOLDER=$HOME/conversion_files/uploads
export CONV_PROCESSED_FOLDER=$HOME/conversion_files/processed
export CONV_SQLALCHEMY_DATABASE_URI='postgresql://conversor:conversor1@192.168.56.133:5432/conversordb'
export CONV_REDIS_QUEUE='colatareas'
export CONV_ALLOWED_EXTENSIONS=mp3,acc,ogg,wav,wma

export CONV_APP_HOME=$HOME/conversor_app/Proyecto-Grupo7-202120
export CONV_APP_LOGS=$HOME/conversion_logs

export CONV_SQLALCHEMY_ENGINE_LOG_LEVEL=INFO
export CONV_APP_LOG_LEVEL=INFO

export PATH=$PATH:$CONV_APP_HOME

cd ~
mkdir conversion_files
cd conversion_files
mkdir processed
mkdir uploads

cp ~/conversor_app/Proyecto-Grupo7-202120/sample_files/* ~/conversion_files/uploads

cd ~
mkdir conversion_logs
