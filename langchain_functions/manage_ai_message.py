from langchain_functions.create_ai_message import create_chat_session

#Constuimos el template, especificandole cuales son las variables de entrada y cual es el texto que tiene que usar
def generate_response(telefonoCliente, human_message):

    ai_message = create_chat_session(telefonoCliente, human_message)

    return ai_message.rstrip("Asistente: ")


