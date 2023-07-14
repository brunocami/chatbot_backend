from datetime import datetime, timedelta

def is_message_old(timestamp):
    # Obtener la fecha y hora actual
    now = datetime.now()

    # Convertir el timestamp a formato de fecha y hora
    message_time = datetime.fromtimestamp(timestamp)

    # Calcular la diferencia de tiempo entre el mensaje y el momento actual
    time_difference = now - message_time

    # Verificar si han pasado más de 24 horas (1 día)
    if time_difference > timedelta(hours=1):
        return True
    else:
        return False