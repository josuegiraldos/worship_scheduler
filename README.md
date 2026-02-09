# 🎹 Gestor Automatizado de Cronogramas de Alabanza

> **Un sistema ETL automatizado para la gestión, rotación y asignación inteligente de músicos, construido con Python y Pandas.**

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-green) ![Status](https://img.shields.io/badge/Status-Production-brightgreen)

## 📖 Descripción del Proyecto

Este proyecto nació de la necesidad de optimizar la gestión de un equipo de alabanza de más de 20 integrantes. La asignación manual generaba errores humanos, repetición de músicos y falta de trazabilidad histórica.

El sistema actúa como un **Asistente Inteligente** que:
1.  **Extrae** la disponibilidad y roles de una base de datos (Excel).
2.  **Transforma** los datos aplicando reglas de negocio complejas (descansos, rotación de líderes, equidad).
3.  **Carga** los resultados en un reporte histórico (Excel Maestro) y exporta el cronograma automáticamente a WhatsApp.

## 🚀 Características Principales

* **🔄 Lógica de Rotación Inteligente:** Algoritmo que asegura que los líderes de alabanza no repitan consecutivamente y que los músicos tengan periodos de descanso adecuados.
* **🛡️ Algoritmo de "Rescate" (Plan B):** Implementación de una lógica de *fallback*. Si el filtro estricto no encuentra candidatos disponibles, el sistema relaja las restricciones automáticamente para garantizar que ningún puesto quede vacío ("Pendiente").
* **💾 Persistencia de Datos:** Uso de archivos JSON para dotar al programa de "memoria", permitiéndole recordar quién tocó la semana pasada para tomar decisiones futuras.
* **📊 Integridad de Datos:** Sistema de validación de duplicados que detecta si un cronograma ya existe en el Histórico Maestro, ofreciendo opciones de sobrescritura o preservación de datos.
* **📱 Automatización de Salidas:** Generación automática de enlaces para envío de cronogramas vía WhatsApp y actualización de bitácora en Excel.

## 🛠️ Tecnologías Utilizadas

* **Python:** Lenguaje principal.
* **Pandas:** Manipulación de DataFrames, limpieza de datos y operaciones ETL (Extract, Transform, Load).
* **OpenPyXL:** Motor de escritura para archivos Excel.
* **JSON:** Gestión de almacenamiento de estados (memoria del programa).
* **OS/Sys:** Automatización de tareas del sistema operativo.

## 📂 Estructura del Proyecto

El código sigue una arquitectura modular para facilitar el mantenimiento y la escalabilidad:

```bash
📁 Worship-Scheduler/
│
├── 📁 src/
│   ├── main.py          # Punto de entrada. Orquestador del flujo.
│   ├── scheduler.py     # Lógica algorítmica y reglas de asignación.
│   └── database.py      # Capa de manejo de datos (Lectura/Escritura Excel & JSON).
│
├── 📁 data/
│   ├── 📁 input/        # Fuente de datos (integrantes.xlsx).
│   └── 📁 output/       # Resultados (Cronograma_Maestro.xlsx, mensajes).
│
└── README.md            # Documentación del proyecto.
```

## 📊 Diccionario de Datos (Estructura de `integrantes.xlsx`)

Para que el algoritmo de asignación y la carga de datos funcionen correctamente, el archivo Excel de entrada debe contar con las siguientes columnas exactas:

| Columna | Descripción |
| :--- | :--- |
| **Lideres** | Cantantes capacitados para dirigir la alabanza. |
| **Voces** | Cantantes principales asignados para el servicio. |
| **Apoyo** | Voces de acompañamiento y coros. |
| **Piano** | Músicos encargados del teclado/piano. |
| **Bajo** | Músicos encargados del bajo eléctrico. |
| **Bateria** | Músicos encargados de la batería. |
| **Congas** | Músicos encargados de la percusión (Congas/Bongós). |
| **Guitarra** | Músicos encargados de la guitarra (Acústica/Eléctrica). |

> **Nota:** El programa ignora las celdas vacías y limpia automáticamente los espacios en blanco al inicio o al final de los nombres.

## 🖼️ Vista Previa del Resultado

Al ejecutar el sistema, se genera automáticamente un mensaje con formato profesional para WhatsApp y se actualiza la bitácora en Excel:

| Notificación de WhatsApp | Historial Maestro (Excel) |
| :---: | :---: |
| ![WhatsApp Preview](assets/preview-whatsapp.png) | ![Excel Preview](assets/preview-excel.png) |

> **Nota:** Las imágenes de arriba son ejemplos del formato de salida generado por el script.

El sistema genera un mensaje formateado listo para ser enviado por redes sociales:

> 📢 **CRONOGRAMA DE ALABANZA** 📢
> 
> **Jueves, 12 Febrero 2026**
> *Piano🎹:* Juan Pérez.
> *Bateria🥁:* Andrés López.
> ... (etc)

## 🧠 Lógica de Negocio y Algoritmos

El corazón del proyecto reside en `scheduler.py`. El proceso de asignación sigue estos pasos:

1.  **Filtrado Inicial:** Se excluyen músicos que tocaron el servicio inmediatamente anterior (regla de descanso).
2.  **Asignación Prioritaria:** Se asignan roles críticos (Piano, Voz Líder) bajo reglas estrictas.
3.  **Gestión de Bolsas (Pools):** Se utilizan "bolsas semanales" para evitar que un músico repita instrumento en la misma semana, a menos que sea estrictamente necesario.
4.  **Manejo de Excepciones:** Se implementan cuotas fijas para casos especiales (ej. pianista principal).

### El Reto de los Datos Duplicados

En el módulo `database.py`, se implementó una lógica de protección de datos:
* Al intentar guardar, el sistema compara las fechas nuevas con el histórico usando `.isin()`.
* Si detecta conflicto, solicita intervención humana: **¿Sobrescribir, Posponer o Cancelar?**
* Esto asegura que el *Cronograma Maestro* sea una fuente única de verdad (SSOT).

## 🔧 Instalación y Uso

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/tu-usuario/worship-scheduler.git](https://github.com/tu-usuario/worship-scheduler.git)
    ```

2.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configurar datos:**
    Asegúrate de tener el archivo `integrantes.xlsx` en la carpeta `data/input/`.

4.  **Ejecutar:**
    ```bash
    python src/main.py
    ```
## ⚙️ Configuración Requerida

Por motivos de seguridad y privacidad, el sistema no incluye un número de teléfono preconfigurado. Para que la función de notificación automática funcione, debes:

1. Abrir el archivo `src/database.py`.
2. Buscar la función `generar_texto_whatsapp`.
3. Localizar la variable `numero_destino`.
4. Ingresar el número en formato internacional (ej: `"573001234567"` para Colombia).

> **Nota:** Se recomienda el uso de variables de entorno para manejar datos sensibles en entornos de producción.

## 📈 Próximos Pasos (Roadmap)

- [ ] Implementar un dashboard de análisis con **Matplotlib** para visualizar estadísticas de participación.
- [ ] Migrar la persistencia de datos de Excel/JSON a una base de datos **SQLite**.
- [ ] Crear una interfaz gráfica (GUI) o web sencilla.

## 👤 Autor

**Josué Gabriel Giraldo Suárez**

---
*Desarrollado con pasión por la música y los datos.* 🎶👨‍💻