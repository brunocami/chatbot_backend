#CONECTAMOS A LA BASE DE DATOS
from flask import jsonify
import mysql.connector
from config import Config

class Mensaje:
    def __init__(self, nombre, edad, servicio, visita):
        self.nombre = nombre
        self.edad = edad
        self.servicio = servicio
        self.visita = visita


def detectar_mensaje(texto, telefonoCliente):
    print(texto)
    if "||" in texto:
        inicio = texto.find("||") + 2
        fin = texto.rfind("||")
        objeto = texto[inicio:fin].strip().split("||")
        nombre = objeto[0].strip()
        edad = objeto[1].strip()
        DNI = objeto[2].strip()
        servicio = objeto[3].strip()
        visita = objeto[4].strip()

        #CONECTAMOS CON LA BASE DE DATOS
        db = mysql.connector.connect(
            host = Config.DATABASE.HOST,
            user = Config.DATABASE.USER,
            database=Config.DATABASE.DATABASE
        )

        cursor = db.cursor()

        sql = ("INSERT INTO visitas"+ 
                "(nombre,edad,servicio      ,DNI   ,dia, telefono) VALUES "+
                "('"+nombre+"'   ,'"+edad+"','"+servicio+"' ,'"+DNI+"','"+visita+"','"+telefonoCliente+"');")
        cursor.execute(sql)
        db.commit()

        # CERRAMOS EL CURSOR Y LA CONEXION CON LA BASE DE DATOS
        cursor.close()
        db.close()
