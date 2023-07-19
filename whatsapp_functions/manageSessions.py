from time import sleep


def delete_active_session(active_session, telefonoCliente):

    if telefonoCliente not in active_session:
    # Crear una nueva sesión para el número de teléfono
        active_session[telefonoCliente] = {
            'conversation_initialized': True,
        }

    sleep(86400)  # Esperamos 24 horas (86400 segundos)
    if telefonoCliente in active_session:
        active_session.pop(telefonoCliente)