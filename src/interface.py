from datetime import datetime
from src.database import cargar_historico_maestro, MESES
from src.analisis import obtener_conteo_mensual, generar_grafica_reporte

def menu_reportes():
    df_maestro = cargar_historico_maestro()
    
    if df_maestro.empty:
        return

    while True:
        print("\n" + "="*40)
        print("📊 MÓDULO DE ANÁLISIS - WORSHIP SCHEDULER")
        print("="*40)
        print("1. Reporte rápido (rol, mes actual)")
        print("2. Reporte personalizado (Elegir rol y mes)")
        print("3. Volver al inicio")
        
        opcion = input("\nSelecciona una opción: ")
        
        if opcion == "1":
            rol = input("Ingrese el rol (Lider, Apoyos, Piano, Guitarra, Bajo, Bateria, Congas): ").capitalize()
            hoy = datetime.now()
            mes_actual = MESES[hoy.month - 1]
            anio_actual = hoy.year
            
            conteo = obtener_conteo_mensual(df_maestro, mes_actual, anio_actual, rol)
            if conteo is not None:
                generar_grafica_reporte(conteo, mes_actual, anio_actual, rol)
        
        elif opcion == "2":
            print("\n--- Configuración de Reporte ---")
            rol = input("Ingrese el rol (Lider, Apoyos, Piano, Guitarra, Bajo, Bateria, Congas): ").capitalize()
            mes = input("Ingrese el mes (Enero, Febrero...): ").capitalize()
            anio_input = input("Ingrese el año (presione Enter para 2026): ")
            anio = int(anio_input) if anio_input else 2026
            
            conteo = obtener_conteo_mensual(df_maestro, mes, anio, rol)
            if conteo is not None:
                generar_grafica_reporte(conteo, mes, anio, rol)
            else:
                print(f"\n❌ No hay datos para {rol} en {mes} {anio}.")
        
        elif opcion == "3":
            break
        else:
            print("⚠️ Opción no válida.")