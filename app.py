from flask import Flask, request, jsonify
from flask_cors import CORS
from db_functions.saveMessageDb import save_message_in_db
from langchain_functions.SalesGPT import sales_agent
from db_functions.users import postUser, getUser
from schedule_functions.message import detectar_mensaje

app = Flask(__name__)
CORS(app)

# Variable para realizar el seguimiento del estado de la conversación
conversation_initialized = False

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
    global conversation_initialized  # Declarar la variable como global

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
    
    dataType = data['entry'][0]['changes'][0]['value']['messages'][0]['type']
    if dataType == "text":
        #EXTRAEMOS EL NUMERO DE TELEFONO Y EL MANSAJE
        telefonoCliente=data['entry'][0]['changes'][0]['value']['messages'][0]['from']
        #EXTRAEMOS EL TELEFONO DEL CLIENTE
        message=data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
        #EXTRAEMOS EL ID DE WHATSAPP DEL ARRAY
        idWA=data['entry'][0]['changes'][0]['value']['messages'][0]['id']
        #EXTRAEMOS EL TIEMPO DE WHATSAPP DEL ARRAY
        timestamp=data['entry'][0]['changes'][0]['value']['messages'][0]['timestamp']
        #SI HAY UN MENSAJE

        # SI LA CONVERSACION NO HABIA SIDO INICIALIZADA
        if not conversation_initialized:
            # INICIO AGENTE 
            sales_agent.seed_agent()  # Se ejecuta solo una vez al inicio
            conversation_initialized = True
        
        # MENSAJE DEL CLIENTE
        sales_agent.human_step(message)  # Se ejecuta cada vez que llega un mensaje
        # FUNCION DE LANGCHAIN
        ai_message = str(sales_agent._call(inputs={}))
        # ESTADO DE LA CONVERSACION
        current_conversation_stage = str(sales_agent.determine_conversation_stage())

        if current_conversation_stage == 'Terminar la conversacion: una vez que el cliente haya decidido acercarse a la tiene o pagar online despidete cordialmente y termina la conversacion.':
            print(current_conversation_stage)
            print("fin de la conversacion")
        # GUARDAR MENSAJE EN DB Y ENVIARLO POR WHAPP
        save_message_in_db(ai_message,idWA,timestamp,telefonoCliente,message, current_conversation_stage)

        detectar_mensaje(ai_message, telefonoCliente)
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
        return message
    return data

# INICIAMOS FLASK
if __name__ == "__main__":
    app.run(debug=True, port=8000)
