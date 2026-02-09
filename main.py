from src.scheduler import crear_cronograma
from src.database import generar_texto_whatsapp, guardar_en_excel_maestro

# Definición de los servicios de la semana
servicios_semana = ["Jueves", "Sabado", "Dominical", "Domingo tarde"]

# 1. Generar el cronograma (incluye lógica de memoria y rescate de músicos)
df_resultado = crear_cronograma(servicios_semana)

# 2. Generar salidas (WhatsApp y Excel Histórico)
generar_texto_whatsapp(df_resultado)
guardar_en_excel_maestro(df_resultado)

# 3. Mostrar resultado en consola
print("\n--- CRONOGRAMA DE ALABANZA ---")
print(df_resultado)