import os
import json
import pandas as pd
from urllib.parse import quote
from datetime import datetime, timedelta

# Configuración de rutas
CARPETA_DATA = os.path.join(os.path.dirname(__file__), "..", "data")
RUTA_INPUT = os.path.join(CARPETA_DATA, "input")
CARPETA_OUTPUT = os.path.join(CARPETA_DATA, "output")
RUTA_INTEGRANTES = os.path.join(RUTA_INPUT, "integrantes.xlsx")
RUTA_JSON = os.path.join(CARPETA_OUTPUT, "memoria_alabanza.json")
RUTA_WHATSAPP = os.path.join(CARPETA_OUTPUT, "mensaje_whatsapp.txt")
RUTA_EXCEL_MAESTRO = os.path.join(CARPETA_OUTPUT, "Cronograma_Maestro.xlsx")

# Crear carpetas si no existen
if not os.path.exists(CARPETA_DATA):
    os.makedirs(CARPETA_DATA)


def cargar_memoria():
    try:
        with open(RUTA_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def guardar_memoria(nuevo_historial):
    if not os.path.exists(CARPETA_OUTPUT):
        os.makedirs(CARPETA_OUTPUT)

    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump(nuevo_historial, f, indent=4, ensure_ascii=False)


def cargar_integrantes():
    if not os.path.exists(RUTA_INTEGRANTES):
        print(f"⚠️ Error: No se encontró el archivo en {RUTA_INTEGRANTES}")
        return {}

    df = pd.read_excel(RUTA_INTEGRANTES)
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    integrantes = {}
    for columna in df.columns:
        integrantes[columna] = df[columna].dropna().tolist()

    return integrantes


def generar_texto_whatsapp(df):
    url_base = "whatsapp://send?phone="
    # Agregar el número telefónico de destino
    numero_destino = ""
    param_txt = "&text="
    hoy = datetime.now()
    
    # Calcular próximo jueves
    dias_hasta_jueves = (3 - hoy.weekday() + 7) % 7
    fecha_base = hoy + timedelta(days=dias_hasta_jueves)

    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
             
    f_formato = lambda d: f"{d.day:02d} {meses[d.month-1]} {d.year}"

    fechas = {
        "Jueves": f_formato(fecha_base),
        "Sabado": f_formato(fecha_base + timedelta(days=2)),
        "Dominical": f_formato(fecha_base + timedelta(days=3)),
        "Domingo tarde": f_formato(fecha_base + timedelta(days=3)),
    }

    contenido = "📢 *CRONOGRAMA DE ALABANZA* 📢\n\n"
    for _, fila in df.iterrows():
        servicio = fila["Servicio"]
        contenido += f"*{servicio}, {fechas.get(servicio)}*\n"
        contenido += f"*Piano🎹:* {fila['Piano']}.\n"
        contenido += f"*Bateria🥁:* {fila['Bateria']}.\n"
        contenido += f"*Guitarra🎸:* {fila['Guitarra']}.\n"
        contenido += f"*Bajo🎸:* {fila['Bajo']}.\n"
        contenido += f"*Congas🪘:* {fila['Congas']}.\n"
        contenido += f"*Voz líder🎤:* {fila['Lider']}.\n"
        contenido += f"*Voces de apoyo:*\n"
        
        for apoyo in fila["Apoyos"].split(", "):
            if apoyo != "Pendiente":
                contenido += f"🎤 {apoyo}.\n"
        contenido += "\n" + "—" * 15 + "\n\n"

    with open(RUTA_WHATSAPP, "w", encoding="utf-8") as f:
        f.write(contenido)

    mensaje_codificado = quote(contenido)
    url_final = f"{url_base}{numero_destino}{param_txt}{mensaje_codificado}"

    os.system(f"open '{url_final}'")
    os.system(f"open '{RUTA_WHATSAPP}'")
    
    return RUTA_WHATSAPP


def guardar_en_excel_maestro(df_nuevo):
    df_temp = df_nuevo.copy()
    hoy = datetime.now()
    dias_hasta_jueves = (3 - hoy.weekday() + 7) % 7
    fecha_base = hoy + timedelta(days=dias_hasta_jueves)

    f_formato = lambda d: f"{d.day:02d}/{d.month:02d}/{d.year}"

    fecha_servicio = {
        "Jueves": f_formato(fecha_base),
        "Sabado": f_formato(fecha_base + timedelta(days=2)),
        "Dominical": f_formato(fecha_base + timedelta(days=3)),
        "Domingo tarde": f_formato(fecha_base + timedelta(days=3)),
    }
    
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", 
             "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    nombre_mes = meses[hoy.month - 1]

    df_temp.insert(0, "Fecha_registro", hoy.strftime("%Y-%m-%d"))
    df_temp.insert(1, "Mes", nombre_mes)
    df_temp.insert(2, "Fecha_servicio", df_temp["Servicio"].map(fecha_servicio))

    if os.path.exists(RUTA_EXCEL_MAESTRO):
        df_historial = pd.read_excel(RUTA_EXCEL_MAESTRO)
        duplicados = df_temp[df_temp["Fecha_servicio"].isin(df_historial["Fecha_servicio"])]
        
        if not duplicados.empty:
            print("¡Alerta! Hay filas duplicadas.")
            res = input("¿Desea sobreescribir los datos? Y/N: ")
            
            if res.upper() == "Y":
                df_historial_limpio = df_historial[~df_historial["Fecha_servicio"].isin(df_temp["Fecha_servicio"])]
                df_total = pd.concat([df_historial_limpio, df_temp], ignore_index=True)
                print("✅ Se sobrescribieron los datos.")
            else:
                print("❌No se sobreescribieron los datos.")
                return
        else:
            df_total = pd.concat([df_historial, df_temp], ignore_index=True)
    else:
        df_total = df_temp

    try:
        df_total.to_excel(RUTA_EXCEL_MAESTRO, index=False)
        print("✅ ¡Excel guardado con éxito!")
    except PermissionError:
        print("❌ ERROR: Cierra el archivo Excel y vuelve a intentarlo.")