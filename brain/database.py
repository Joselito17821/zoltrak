import os
import psycopg2
from dotenv import load_dotenv

# Función para conectar a la base de datos PostgreSQL
def conectar_base_de_datos():
    load_dotenv()
    host = os.getenv("DB_HOST")
    puerto = os.getenv("DB_PORT")
    nombre_db = os.getenv("DB_NAME")
    usuario = os.getenv("DB_USER")
    contraseña = os.getenv("DB_PASSWORD")

    return psycopg2.connect(

        host=host,
        port=puerto,
        dbname=nombre_db,
        user=usuario,
        password=contraseña
)

# Función para guardar mensajes (tabla mensajes) en la base de datos
def guardar_mensajes(rol, contenido):
    conexion = conectar_base_de_datos()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO mensajes (rol, contenido) VALUES (%s, %s)",
        (rol, contenido)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para obtener el historial de mensajes (tabla mensajes) de la base de datos
def obtener_historial_mensajes():
    conexion = conectar_base_de_datos()
    cursor = conexion.cursor()

    cursor.execute("SELECT rol, contenido FROM mensajes ORDER BY id_message ASC")
    historial = cursor.fetchall()

    cursor.close()
    conexion.close()

    return historial

# Función para guardar hechos (tabla hechos) en la base de datos
def guardar_hecho(categoria, valor):
    conexion = conectar_base_de_datos()
    cursor = conexion.cursor()

    cursor.execute(
        "INSERT INTO hechos (categoria, valor) VALUES (%s, %s)",
        (categoria, valor)
    )

    conexion.commit()
    cursor.close()
    conexion.close()

# Función para obtener el historial de hechos (tabla hechos) de la base de datos
def obtener_historial_hechos():
    conexion = conectar_base_de_datos()
    cursor = conexion.cursor()

    cursor.execute("SELECT categoria, valor FROM hechos ORDER BY id_hecho ASC")
    historial = cursor.fetchall()

    cursor.close()
    conexion.close()

    return historial