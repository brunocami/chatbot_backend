#CONECTAMOS A LA BASE DE DATOS
from flask import jsonify
import mysql.connector
from config import Config
from whatsapp_functions.mesage_date import is_message_old
from whatsapp_functions.sendMessage import enviar

#SI HAY UN MENSAJE
def save_message_in_db(mensaje,idWA,timestamp,telefonoCliente,message):

    is_old = is_message_old(int(timestamp))

    if is_old:
        print('is old')
    else: 
        if mensaje is not None:
            #CONECTAMOS CON LA BASE DE DATOS
            db = mysql.connector.connect(
                host = Config.DATABASE.HOST,
                user = Config.DATABASE.USER,
                database=Config.DATABASE.DATABASE
            )
            cursor = db.cursor()
            cursor.execute("SELECT count(id) AS cantidad FROM historial_de_conversacion WHERE id_wa='" + idWA + "';")

            cantidad,=cursor.fetchone()
            cantidad=str(cantidad)
            cantidad=int(cantidad)

            if cantidad==0 :
                sql = ("INSERT INTO historial_de_conversacion"+ 
                "(user_message,ai_message,id_wa      ,timestamp_wa   ,telefono_wa) VALUES "+
                "('"+message+"'   ,'"+mensaje+"','"+idWA+"' ,'"+timestamp+"','"+telefonoCliente+"');")
                cursor.execute(sql)
                db.commit()

                # CERRAMOS EL CURSOR Y LA CONEXION CON LA BASE DE DATOS
                cursor.close()
                db.close()
                # ENVIAR EL MENSAJE AL CLIENTE
                enviar(telefonoCliente,mensaje,Config.WHATSAPP.TOKEN,Config.WHATSAPP.ID_NUMERO_TELEFONO)


            # RETORNAMOS EL STATUS EN UN JSON
            return jsonify({"status": "success"}, 200)