from datetime import datetime
from difflib import get_close_matches
import unicodedata

from src.database import cargar_historico_maestro, MESES, cargar_integrantes
from src.analisis import obtener_conteo_mensual, generar_grafica_reporte

# Obtenemos el diccionario con toda la información
datos_integrantes = cargar_integrantes()

# Extraemos las llaves (roles) y las convertimos en una lista
ROLES_VALIDOS = list(datos_integrantes.keys())
roles_texto = ", ".join(ROLES_VALIDOS)


def eliminar_tildes(texto):
    texto_normalizado = unicodedata.normalize("NFD", texto)
    solo_base = "".join(c for c in texto_normalizado if unicodedata.category(c) != "Mn")
    return solo_base


def obtener_entrada_validada(mensaje, lista_valida, nombre_categoria):
    # Creamos el mapeo (llave limpia: valor real)
    mapeo = {
        eliminar_tildes(r).lower(): r for r in lista_valida
        }
    
    # Creamos la lista usando las llaves del mapeo (ya limpias)
    opciones_busqueda = list(mapeo.keys())
    
    # Texto que el usuario verá entre paréntesis
    opciones_texto = ", ".join(lista_valida)

    while True:
        entrada_usuario = input(f"{mensaje} ({opciones_texto}): ").strip()
        entrada_limpia = eliminar_tildes(entrada_usuario).lower()

        # Verificación directa en el "traductor"
        if entrada_limpia in mapeo:
            return mapeo[entrada_limpia]
            

        # Si no acierta en el input, buscamos una sugerencia
        sugerencias = get_close_matches(entrada_limpia, opciones_busqueda, n = 1, cutoff = 0.6)

        if sugerencias:
            sugerencia_limpia = sugerencias[0]
            sugerencia_final = mapeo[sugerencia_limpia]
            confirmacion = input(f"🤔 No encontré '{entrada_usuario}', ¿quisiste decir '{sugerencia_final}'? (S/N): ").upper()

            if confirmacion == "S":
                return sugerencia_final
            
        print(f"\n❌ '{entrada_usuario}' no es un/a {nombre_categoria} válido/a.")
        print(f"Opciones de {nombre_categoria} disponibles ({opciones_texto}): ")
        
def obtener_anio_validado(mensaje, default = datetime.now().year):
    while True:
        entrada = input(f"{mensaje} (presione Enter para {default}): ").strip()
        
        # Si el usuario presiona Enter, usamos el año por defecto
        if not entrada:
            return default
        
        try:
            anio = int(entrada)
            # Validar que sea un año razonable
            if 2000 <= anio <= 2100:
                return anio
            else:
                print("❌ Por favor, ingrese un año válido.")
        except ValueError:
            print(f"❌ '{entrada}' no es un número válido. Intenta de nuevo.")

def menu_reportes():
    df_maestro = cargar_historico_maestro()

    if df_maestro.empty:
        return

    while True:
        print("\n" + "=" * 40)
        print("📊 MÓDULO DE ANÁLISIS - WORSHIP SCHEDULER")
        print("=" * 40)
        print("1. Reporte rápido (rol, mes actual)")
        print("2. Reporte personalizado (Elegir rol y mes)")
        print("3. Volver al inicio")

        opcion = input("\nSelecciona una opción: ")

        if opcion == "1":
            hoy = datetime.now()
            mes_actual = MESES[hoy.month - 1]
            anio_actual = hoy.year
            
            rol = obtener_entrada_validada("Ingrese el rol", ROLES_VALIDOS, "rol")

            conteo = obtener_conteo_mensual(df_maestro, mes_actual, anio_actual, rol)
            if conteo is not None:
                generar_grafica_reporte(conteo, mes_actual, anio_actual, rol)

        elif opcion == "2":
            print("\n--- Configuración de Reporte ---")
            rol = obtener_entrada_validada("Ingrese el rol", ROLES_VALIDOS, "rol")
            mes = obtener_entrada_validada("Ingrese el mes", MESES, "mes")
            anio = obtener_anio_validado("Ingrese el año", default = datetime.now().year)

            conteo = obtener_conteo_mensual(df_maestro, mes, anio, rol)
            if conteo is not None:
                generar_grafica_reporte(conteo, mes, anio, rol)
            else:
                print(f"\n❌ No hay datos para {rol} en {mes} {anio}.")

        elif opcion == "3":
            break
        else:
            print("⚠️ Opción no válida.")
