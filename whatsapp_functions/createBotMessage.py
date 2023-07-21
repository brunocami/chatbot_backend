from time import sleep

def createMessage(mensajes, mensajes_enviados):
    # ESPERO UN MINUTO Y CONCATENO TODOS LOS MENSAJES QUE LLEGUEN EN ESE PERIODO EN UNA VARIABLE
    sleep(10)

    # Si los mensajes no se han enviado y hay mensajes en la cola, los enviamos
    if not mensajes_enviados and not mensajes.empty():
        message_chain = ""
        while not mensajes.empty():
            message_chain += mensajes.get() + "\n"
        
        # # Para utilizar funcionalidades de Flask, debemos activar el contexto de la aplicación
        # with current_app.app_context():
        print(message_chain)
            
        mensajes_enviados = True