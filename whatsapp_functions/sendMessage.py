from heyoo import WhatsApp

def enviar(telefonoRecibe,respuesta,token,idNumeroTelefono):

  #INICIALIZAMOS ENVIO DE MENSAJES (token de acceso a facebook, id numero de telefono whatsapp business)
  mensajeWa=WhatsApp(token,idNumeroTelefono)
  telefonoRecibe=telefonoRecibe.replace("54911","541115")
  #ENVIAMOS UN MENSAJE DE TEXTO
  mensajeWa.send_message(respuesta,telefonoRecibe)