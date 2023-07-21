from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_functions.SalesGPT import sales_agent
from db_functions.users import postUser, getUser
from whatsapp_functions.createBotMessage import createMessage 
from whatsapp_functions.manageSessions import delete_active_session
from schedule_functions.message import detectar_mensaje
from db_functions.saveMessageDb import save_message_in_db
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
            sales_agent.seed_agent(telefonoCliente)  # Se ejecuta solo una vez al inicio

        # Agregar el mensaje a la cola
        mensajes.put(message)
        # ESPERO UN MINUTO Y CONCATENO TODOS LOS MENSAJES QUE LLEGUEN EN ESE PERIODO EN UNA VARIABLE
        sleep(10)
        # Si los mensajes no se han enviado y hay mensajes en la cola, los enviamos
        if not mensajes_enviados and not mensajes.empty():
            message_chain = ""
            while not mensajes.empty():
                message_chain += mensajes.get() + " "
            # MENSAJE DEL CLIENTE
            sales_agent.human_step(message_chain, telefonoCliente)  # Se ejecuta cada vez que llega un mensaje
            # FUNCION DE LANGCHAIN
            ai_message = str(sales_agent.step(telefonoCliente))
            # ESTADO DE LA CONVERSACION
            current_conversation_stage = str(sales_agent.determine_conversation_stage(telefonoCliente))
            # GUARDAR MENSAJE EN DB Y ENVIARLO POR WHAPP
            save_message_in_db(ai_message, idWA, timestamp, telefonoCliente, message_chain, current_conversation_stage)
           
            detectar_mensaje(ai_message, telefonoCliente)
            mensajes_enviados = True

    else: 
        messageType=data['entry'][0]['changes'][0]['value']['messages'][0]['type']
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
