import os
import pandas as pd
import matplotlib.pyplot as plt
from src.database import CARPETA_OUTPUT

CARPETA_REPORTES = os.path.join(CARPETA_OUTPUT, "reportes")

def obtener_conteo_mensual(df, mes, anio, rol):
    df["Fecha_servicio"] = pd.to_datetime(df["Fecha_servicio"], dayfirst = True)
    
    # Filtramos por mes y año
    df_mes = df[(df["Mes"] == mes) & (df["Fecha_servicio"].dt.year == anio)]
    
    if df_mes.empty:
        print(f"⚠️ Aviso: No se encontraron registros para {mes} de {anio}.")
        return None # Salimos de la función para no intentar graficar nada
    
    # Si el rol es el de "Apoyos", primero se procesan los datos porque hay 
    if rol == "Apoyos":
        serie = df_mes[rol].str.split(",").explode().str.strip()
    else:
        serie = df_mes[rol]
        
    return serie.value_counts().sort_values(ascending = False)
    
def generar_grafica_reporte(conteo, mes, anio, rol):
    # Configurar la visualización
    nombres = conteo.index.astype(str)
    cantidades = conteo.values.tolist()

    # Dibujar barras
    fig, ax = plt.subplots(figsize = (10, 5))
    ax.bar(nombres, cantidades, color = "#3498db")
    
    # Personalizar el gráfico
    ax.set_title(f"Participación de {rol} - {mes}, {anio}", fontsize = 14, fontweight = "bold")
    ax.set_xlabel("Integrantes", fontsize = 12)
    ax.set_ylabel("Cantidad de servicios", fontsize = 12)
    # Rotar nombres para que sean legibles
    ax.tick_params(axis = "x", rotation = 45)
    
    # Ajustar márgenes
    plt.tight_layout()
    
    # Guardado automático
    nombre_archivo = f"reporte_{rol}_{mes}_{anio}.png"
    ruta_final = os.path.join(CARPETA_REPORTES, nombre_archivo)
    # Siempre se guarda primero
    fig.savefig(ruta_final, dpi = 300, bbox_inches = "tight")
    
    print(f"🖼️ Reporte guardado en: {ruta_final}")
    
    # Y se muestra después
    plt.show()
    pass