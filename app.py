from flask import Flask, request, jsonify
from flask_cors import CORS
from db_functions.users import postUser, getUser
from whatsapp_functions.manageSessions import delete_active_session
from db_functions.saveMessageDb import save_message_in_db
from langchain_functions.manage_ai_message import generate_response
import threading
from time import sleep
from queue import Queue

mensajes = Queue()
mensajes_enviados = False 

app = Flask(__name__)
CORS(app)

active_session = {}

@app.route('/login', methods=['GET'])
def getUsers():
    users = getUser()
    return jsonify(users)

@app.route('/login', methods=['POST'])
def createUsers():
    postUser(request.json['id_user'],request.json['name'],request.json['email'],request.json['password'])
    return jsonify('posteo')

@app.route('/webhook/', methods=['POST','GET'])
def webhook_whatsapp():

    global mensajes
    global mensajes_enviados

    # SI HAY DATOS RECIBIDOS VIA GET
    if request.method == "GET":
        # SI EL TOKEN ES IGUAL AL QUE RECIBIMOS
        if request.args.get('hub.verify_token') == "TokenDeVerificacion":
            # ESCRIBIMOS EN EL NAVEGADOR EL VALOR DEL RETO RECIBIDO DESDE FACEBOOK
            return request.args.get('hub.challenge')
        else:
            # SI NO SON IGUALES RETORNAMOS UN message DE ERROR
            return "Error de autenticación."

    # RECIBIMOS TODOS LOS DATOS ENVIADOS VIA JSON
    data = request.get_json()

    if data['entry'][0]['changes'][0]['value']['messages'][0]['type'] == "text":
        #EXTRAEMOS EL TELEFONO DEL CLIENTE
        telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        #SI HAY UN MENSAJE
        message=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
        idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
        #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
        timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']

        if telefonoCliente not in active_session:
            # Crear una nueva sesión para el número de teléfono
            # Iniciar el temporizador en un hilo separado
            threading.Thread(target=delete_active_session, args=(active_session,telefonoCliente)).start()

        # Agregar el mensaje a la cola
        mensajes.put(message)
        # ESPERO UN MINUTO Y CONCATENO TODOS LOS MENSAJES QUE LLEGUEN EN ESE PERIODO EN UNA VARIABLE
        sleep(5)
        # Si los mensajes no se han enviado y hay mensajes en la cola, los enviamos
        if not mensajes_enviados and not mensajes.empty():
            message_chain = ""
            while not mensajes.empty():
                message_chain += mensajes.get() + " "
            # FUNCION DE LANGCHAIN
            ai_message = generate_response(telefonoCliente, message_chain)
            # GURADAR EL MENSAJE EN LA BASE DE DATOS Y ENVIARLO POR WAPP
            save_message_in_db(ai_message, idWA, timestamp, telefonoCliente, message_chain)
            
            mensajes_enviados = False

    else: 
        #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
        telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        #EXTRAEMOS EL TELEFONO DEL CLIENTE
        message='por favor, enviar mensjaes de texto unicamente'
        #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
        idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
        #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
        timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
    
    return data

# INICIAMOS FLASK
if __name__ == "__main__":
    app.run(debug=True, port=8000)
