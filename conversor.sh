#!/bin/bash

function start_app() {
    
    sudo systemctl start conversion_app
    sudo systemctl start nginx

    sleep 3
    chmod 666 $CONV_APP_HOME/flaskr/conversion_app.sock    

}

function stop_app() {

    sudo systemctl stop conversion_app
    sudo systemctl stop nginx

}

function status_app() {
    sudo systemctl status conversion_app
    sudo systemctl status nginx
}

case "$1" in
    start)   start_app ;;
    stop)    stop_app ;;
    restart) stop_app; start_app ;;
    status) status_app;;
    *) echo "Uso: conversor.sh start|stop|restart|status" >&2
       exit 1
       ;;
esac
