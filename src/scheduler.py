import random
import pandas as pd
from src.database import cargar_integrantes, cargar_memoria, guardar_memoria


def asignar_musico(
    nombre_rol,
    integrantes,
    bolsa_semanal,
    ocupados_hoy,
    i,
    indices_josue,
    pueden_duplicarse,
    instrumentistas_hoy,
):
    """
    Selecciona un músico para un instrumento específico gestionando la bolsa semanal
    y las restricciones de disponibilidad.
    """
    instrumentos_fisicos = ["Piano", "Bajo", "Bateria", "Congas", "Guitarra"]

    # Si la bolsa se vacía, la rellenamos con todos los integrantes
    if len(bolsa_semanal[nombre_rol]) == 0:
        bolsa_semanal[nombre_rol] = list(integrantes[nombre_rol])

    es_disponible = lambda p: (p not in ocupados_hoy) or (
        p in pueden_duplicarse and p not in instrumentistas_hoy
    )

    # Lógica específica para el Piano (Prioridad Josue)
    if nombre_rol == "Piano":
        candidatos = [
            p
            for p in bolsa_semanal["Piano"]
            if es_disponible(p) and (p != "Josue Giraldo" or i in indices_josue)
        ]
        if (
            (i in indices_josue)
            and "Josue Giraldo" in integrantes["Piano"]
            and es_disponible("Josue Giraldo")
        ):
            musico = "Josue Giraldo"
        elif candidatos:
            musico = random.choice(candidatos)
        else:
            musico = "Pendiente asignacion"
    else:
        # Plan A: Buscar en la bolsa semanal
        candidatos = [p for p in bolsa_semanal[nombre_rol] if es_disponible(p)]
        
        # Plan B: Si la bolsa falla, buscar en la lista general (Rescate)
        if not candidatos:
            candidatos = [p for p in integrantes[nombre_rol] if es_disponible(p)]
            
        musico = random.choice(candidatos) if candidatos else "Pendiente asignacion"

    # Actualizar listas de control
    if musico != "Pendiente asignacion":
        ocupados_hoy.append(musico)
        proximos_servicios_josue = [idx for idx in indices_josue if idx > i]

        # Solo sacamos de la bolsa si no es Josue cumpliendo su cuota fija
        if not (
            musico == "Josue Giraldo"
            and nombre_rol == "Piano"
            and proximos_servicios_josue
        ):
            if musico in bolsa_semanal[nombre_rol]:
                bolsa_semanal[nombre_rol].remove(musico)

        if nombre_rol in instrumentos_fisicos:
            instrumentistas_hoy.append(musico)
            
    return musico


def crear_cronograma(lista_servicios):
    """
    Genera el cronograma completo para la lista de servicios proporcionada.
    """
    integrantes_alabanza = cargar_integrantes()
    cronograma_anterior = cargar_memoria()
    data, nuevo_historial = [], {}

    # Determinar servicios fijos de Josue
    if len(lista_servicios) > 2:
        indices_josue = random.sample(range(len(lista_servicios)), 2)
    else:
        indices_josue = []

    # Preparar pools de músicos
    pool_apoyo_total = list(
        integrantes_alabanza["Lideres"]
        + integrantes_alabanza["Voces"]
        + integrantes_alabanza["Apoyo"]
    )
    conteo_apoyos = {persona: 0 for persona in pool_apoyo_total}

    bolsa_lideres = list(integrantes_alabanza["Lideres"])
    random.shuffle(bolsa_lideres)

    bolsa_voces_expertos = list(
        integrantes_alabanza["Lideres"] + integrantes_alabanza["Voces"]
    )

    bolsas_inst = {
        rol: list(integrantes_alabanza[rol])
        for rol in integrantes_alabanza
        if rol not in ["Lideres", "Apoyo"]
    }

    instrumentos = ["Piano", "Guitarra", "Bajo", "Bateria", "Congas"]

    # --- Generación día por día ---
    for i, servicio in enumerate(lista_servicios):
        pueden_duplicarse = ["Orlando Ariza", "Yoanir Hernandez", "Jhonny Ropero"]
        ocupados_hoy, instrumentistas_hoy, descansan_hoy = [], [], []

        # Determinar quién descansa (basado en el día anterior)
        if i > 0:
            anterior = data[i - 1]
            descansan_hoy = [anterior[1]] + anterior[2].split(", ")

        # 1. Asignar Voz Líder
        lider_pasado = cronograma_anterior.get(servicio, {}).get("Lider")
        candidatos_lider = [p for p in bolsa_lideres if p != lider_pasado]
        
        if not candidatos_lider:
            bolsa_lideres = list(integrantes_alabanza["Lideres"])
            random.shuffle(bolsa_lideres)
            candidatos_lider = [p for p in bolsa_lideres if p != lider_pasado]

        voz_lider = random.choice(candidatos_lider)
        bolsa_lideres.remove(voz_lider)
        ocupados_hoy.append(voz_lider)
        conteo_apoyos[voz_lider] += 1

        # 2. Asignar Instrumentos
        asignaciones_hoy = {}
        for instrumento in instrumentos:
            musico = asignar_musico(
                instrumento,
                integrantes_alabanza,
                bolsas_inst,
                ocupados_hoy,
                i,
                indices_josue,
                pueden_duplicarse,
                instrumentistas_hoy,
            )
            asignaciones_hoy[instrumento] = musico

        # 3. Asignar Voces (Expertos)
        candidatos_voces = [
            p
            for p in pool_apoyo_total
            if p in bolsa_voces_expertos
            and p not in ocupados_hoy
            and p not in descansan_hoy
        ]
        
        # Plan B Voces: Buscar refuerzos si faltan candidatos
        if len(candidatos_voces) < 2:
            refuerzos = [
                p
                for p in pool_apoyo_total
                if p in bolsa_voces_expertos
                and p not in ocupados_hoy
                and p not in candidatos_voces
            ]
            candidatos_voces.extend(refuerzos)
            
        random.shuffle(candidatos_voces)
        candidatos_voces.sort(key=lambda p: conteo_apoyos[p])

        seleccionados_voces = candidatos_voces[:2]
        for v in seleccionados_voces:
            conteo_apoyos[v] += 1
        
        # Relleno final si aún faltan
        while len(seleccionados_voces) < 2:
            seleccionados_voces.append("Pendiente voz")

        # 4. Asignar Apoyo (General)
        candidatos_apoyo = [
            p
            for p in integrantes_alabanza["Apoyo"]
            if p not in ocupados_hoy and p not in descansan_hoy
        ]
        
        # Plan B Apoyo: Buscar refuerzos (solo del grupo Apoyo)
        if len(candidatos_apoyo) < 1:
            refuerzos = [
                p
                for p in pool_apoyo_total
                if p in integrantes_alabanza["Apoyo"]
                and p not in ocupados_hoy
                and p not in candidatos_apoyo
            ]
            candidatos_apoyo.extend(refuerzos)
            
        random.shuffle(candidatos_apoyo)
        candidatos_apoyo.sort(key=lambda p: conteo_apoyos[p])

        seleccionados_apoyo = candidatos_apoyo[:1]
        for v in seleccionados_apoyo:
            conteo_apoyos[v] += 1
            
        while len(seleccionados_apoyo) < 1:
            seleccionados_apoyo.append("Pendiente apoyo")

        # Consolidar datos del servicio
        voces_finales = seleccionados_voces + seleccionados_apoyo
        
        fila_data = [
            servicio,
            voz_lider,
            ", ".join(voces_finales),
        ]

        nuevo_historial[servicio] = {
            "Lider": voz_lider,
            "Apoyos": fila_data[2],
        }

        for inst in instrumentos:
            fila_data.append(asignaciones_hoy[inst])
            nuevo_historial[servicio][inst] = asignaciones_hoy[inst]

        data.append(fila_data)

    # Guardar memoria y retornar DataFrame
    guardar_memoria(nuevo_historial)

    cabeceras_fijas = ["Servicio", "Lider", "Apoyos"]
    extras = instrumentos
    lista_completa = cabeceras_fijas + extras
    
    return pd.DataFrame(data, columns=lista_completa)