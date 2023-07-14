import mysql.connector
from config import Config

def postUser(id_user, name, mail, password):
    db = mysql.connector.connect(
        host = Config.DATABASE.HOST,
        user = Config.DATABASE.USER,
        database=Config.DATABASE.DATABASE
    )
    
    cursor = db.cursor()
    sql = ("INSERT INTO users"+ 
        "(id_user,name,mail,password) VALUES "+
        "('"+id_user+"','"+name+"','"+mail+"','"+password+"');")
    cursor.execute(sql)
    db.commit()

    # CERRAMOS EL CURSOR Y LA CONEXION CON LA BASE DE DATOS
    cursor.close()
    db.close()

def getUser():
    db = mysql.connector.connect(
        host = Config.DATABASE.HOST,
        user = Config.DATABASE.USER,
        database=Config.DATABASE.DATABASE
    )
    
    cursor= db.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    # CERRAMOS EL CURSOR Y LA CONEXION CON LA BASE DE DATOS
    cursor.close()
    db.close()
    return users
