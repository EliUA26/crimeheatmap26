import html
import os
import textwrap
from typing import Any

import folium
from folium.plugins import HeatMap, MarkerCluster

from conexiondb import get_connection

MAPA_SALIDA = "MAPA_FINAL_ENTREGA.html"
UBICACION_MAPA = [-25.2822, -57.6359]
ZOOM_INICIAL = 13
TILESET = "cartodbpositron"

COLOR_MAP = {
    "homicidio": "orange",
    "robo": "red",
    "asalto": "red",
    "hurto": "blue",
    "narcotrafico": "green",
    "violencia": "darkpurple",
}


def obtener_color(tipo):
    return COLOR_MAP.get((tipo or "").lower(), "gray")


def obtener_icono(tipo):
    tipo_texto = (tipo or "").lower()

    if "robo" in tipo_texto or "asalto" in tipo_texto:
        return folium.Icon(color="red", icon="user-secret", prefix="fa")
    if "homicidio" in tipo_texto:
        return folium.Icon(color="orange", icon="user-secret", prefix="fa")
    if "droga" in tipo_texto or "narcotrafico" in tipo_texto:
        return folium.Icon(color="green", icon="leaf", prefix="fa")
    if "arma" in tipo_texto:
        return folium.Icon(color="black", icon="gavel", prefix="fa")

    return folium.Icon(color="blue", icon="info-sign")


def limpiar_texto(valor: Any) -> str:
    if valor is None:
        return ""
    return html.escape(str(valor).strip(), quote=True)


def crear_popup(tipo: str, resumen: str, ciudad: str, fecha: str, url: str) -> str:
    tipo_seguro = limpiar_texto(tipo)
    resumen_seguro = limpiar_texto(resumen)
    ciudad_seguro = limpiar_texto(ciudad)
    fecha_seguro = limpiar_texto(fecha)
    url_seguro = limpiar_texto(url)
    color = obtener_color(tipo)

    url_html = (
        f'<div style="margin-top: 10px;"><a href="{url_seguro}" target="_blank" rel="noopener noreferrer" style="color:#333; text-decoration:none;">Fuente</a></div>'
        if url_seguro
        else ""
    )

    return textwrap.dedent(
        f"""
        <div style="width: 250px; font-family: Arial, sans-serif; font-size: 13px;">
            <div style="background-color:{color}; color: white; padding: 8px 10px; border-radius: 6px; text-align: center; font-weight: bold;">
                {tipo_seguro}
            </div>
            <hr style="margin: 8px 0;">
            <div><strong>Ciudad:</strong> {ciudad_seguro}</div>
            <div style="margin-top: 8px;"><strong>Fecha:</strong> {fecha_seguro}</div>
            <div style="margin-top: 8px; color: #333;">{resumen_seguro}</div>
            {url_html}
        </div>
        """
    )


def integrar_todo():
  
    # Usar ruta absoluta basada en la ubicación del script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salida_final = os.path.join(script_dir, 'MAPA_FINAL_ENTREGA.html')
    
    puntos_totales = []
    
    # 1. Crear el mapa base centrado en Asunción
    mapa = folium.Map(location=[-25.2822, -57.6359], zoom_start=13, tiles="cartodbpositron")
    
   
    # Creamos capas separadas para que se puedan apagar y prender
    capa_calor = folium.FeatureGroup(name="Mapa de Calor (Densidad)")
    capa_marcadores = MarkerCluster(name="Incidentes Individuales").add_to(mapa)
    capa_busqueda = folium.FeatureGroup(name="Ciudad").add_to(mapa)

    

    # --- PARTE 1: OBTENER TUS DATOS DESDE POSTGRESQL (LOCAL) ---
    print("📡 Conectando a tu base de datos SQL local...")
    try:
        conn = get_connection()
        cur = conn.cursor()
        query = "SELECT tipo_delito, resumen_breve, ST_Y(geom), ST_X(geom),url_fuente,ciudad,to_char(fecha_evento,'dd/mm/yyy') FROM delitos WHERE geom IS NOT NULL;"
        cur.execute(query)
        mis_datos = cur.fetchall()
        
        

        capas = {}  # guardar capas por tipo
        for tipo, resumen, lat, lng, url,ciudad,fecha in mis_datos:


             # crear capa si no existe
            if tipo not in capas:
                capas[tipo] = folium.FeatureGroup(name=tipo)
                capas[tipo].add_to(mapa)
            
            
           

    # crear capa si no existe
          
            print(tipo)
            print(resumen)
            popup_html = f"""
            <div style="
                width: 250px;
                font-family: Arial;
                font-size: 13px;
            ">

                <div style="
                    background-color:{obtener_color(tipo)};
                    color:white;
                    padding:6px;
                    border-radius:5px;
                    text-align:center;
                    font-weight:bold;
                ">
                    {tipo}
                </div>

                <hr style="margin:6px 0;">

                <b>Ciudad:</b> {ciudad}<br>

                <b>Resumen:</b><br>
                <div style="margin-top:4px; color:#333;">
                    {resumen}
                </div>
                   <div style="margin-top:4px; color:#333;">
                    {fecha}
                </div>
                <div style="margin-top:4px;">
                <a 
                    href="{url}" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    style="
                    color:#333;
                    text-decoration:none;
                    font-size:0.9rem;
                    transition:color 0.2s ease;
                    "
                    onmouseover="this.style.color='#000'; this.style.textDecoration='underline';"
                    onmouseout="this.style.color='#333'; this.style.textDecoration='none';"
                >
                    Fuente
                </a>
                </div>
                

            </div>
            """
            puntos_totales.append([lat, lng])
    
          
            # folium.Marker(
            #     location=[lat, lng],
            #     popup=popup_html,
            #     tooltip=f"{tipo}",
            #     icon=obtener_icono(tipo),
            #     title=f"{1}"
            # ).add_to(capa_marcadores)


            folium.Marker(
                location=[lat, lng],
                popup=popup_html,
                tooltip=tipo,
                icon=obtener_icono(tipo)
            ).add_to(capas[tipo])
            
                
        #     feature = {
        #     "type": "Feature",
        #     "geometry": {
        #         "type": "Point",
        #         "coordinates": [lng, lat]  #  OJO: GeoJSON es [lon, lat]
        #     },
        #     "properties": {
        #         "tipo": tipo,
        #         "resumen": resumen,
        #         "url": url,
        #         "ciudad": ciudad
        #     }
        #     }

        #     features.append(feature)

        # geo_data = {
        #     "type": "FeatureCollection",
        #     "features": features
        # }
            
        # geo_layer = folium.GeoJson(
        #     geo_data,
        #     name="puntos"
        # ).add_to(mapa)
        
        # folium.GeoJson(
        #     geo_data,
        #     name="puntos",
        #     tooltip=folium.GeoJsonTooltip(
        #         fields=["tipo", "ciudad"],
        #         sticky=True
        #     )
        # ).add_to(mapa)
                        
            
        #folium.LayerControl(collapsed=False).add_to(mapa)
        print(f"✅ Se integraron {len(mis_datos)} registros de tu base de datos local.")
        cur.close()
        conn.close()
        # search = Search(
        #     layer=geo_layer,
        #     search_label="ciudad",   # o "ciudad", "resumen"
        #     placeholder="Buscar tipo...",
        #     collapsed=False
        # )

        # search.add_to(mapa)
        mapa.get_root().html.add_child(folium.Element("""
<style>

/* CONTENEDOR */
.leaflet-control-search {
    background: #ffffff !important;
    padding: 10px !important;
    border-radius: 14px !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15) !important;
    border: 1px solid #eaeaea !important;
    display: flex !important;
    align-items: center !important;
}

/* INPUT */
.leaflet-control-search input {
    width: 260px !important;
    height: 40px !important;
    font-size: 14px !important;
    font-family: Arial, sans-serif !important;

    color: #2c3e50 !important;
    background: #ffffff !important;

    border-radius: 10px !important;
    border: 1px solid #ddd !important;

    padding: 0 12px !important;
    margin-right: 6px !important;

    outline: none !important;
}

/* FOCUS INPUT */
.leaflet-control-search input:focus {
    border: 1px solid #000000 !important;
    box-shadow: 0 0 0 3px rgba(0,0,0,0.08) !important;
}

/* BOTÓN SEARCH (FIX ICONO AZUL + CENTRADO) */
.leaflet-control-search .search-button {
    width: 40px !important;
    height: 40px !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    background: #ffffff !important;
    border: 1px solid #ddd !important;
    border-radius: 10px !important;

    box-shadow: none !important;

    color: #000000 !important;
    font-size: 16px !important;
    line-height: 1 !important;

    padding: 0 !important;
}

/* ICONO NEGRO (FORZADO) */
.leaflet-control-search .search-button i,
.leaflet-control-search .search-button::before {
    color: #000000 !important;
}

/* HOVER BOTÓN */
.leaflet-control-search .search-button:hover {
    background: #f5f5f5 !important;
    border-color: #000000 !important;
}

/* RESULTADOS */
.leaflet-control-search .search-tooltip {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: none !important;
    box-shadow: 0 6px 18px rgba(0,0,0,0.15) !important;
}

/* ITEMS */
.leaflet-control-search .search-tip {
    padding: 10px 12px !important;
    font-size: 13px !important;
}

/* HOVER ITEMS */
.leaflet-control-search .search-tip:hover {
    background: #f2f2f2 !important;
}

/* ITEM SELECCIONADO */
.leaflet-control-search .search-tip-select {
    background: #000000 !important;
    color: #ffffff !important;
}

/* RESPONSIVE */
@media (max-width: 768px) {
    .leaflet-control-search input {
        width: 180px !important;
    }
}

</style>
"""))
        legend_html = """
        <div style="
            position: fixed;
            bottom: 40px;
            left: 40px;
            width: 220px;
            background-color: white;
            border-radius: 12px;
            padding: 14px;
            z-index:9999;
            font-size:14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            border: 1px solid #ddd;
        ">

            <div style="
                font-weight:bold;
                margin-bottom:10px;
                font-size:15px;
                color:#2c3e50;
                text-align:center;
            ">
                Tipos de Delito
            </div>

            <div style="margin-bottom:6px;">
                <span style="
                    display:inline-block;
                    width:14px;
                    height:14px;
                    background:red;
                    border-radius:50%;
                    margin-right:8px;
                "></span>
                Robo / Asalto
            </div>

            <div style="margin-bottom:6px;">
                <span style="
                    display:inline-block;
                    width:14px;
                    height:14px;
                    background:orange;
                    border-radius:50%;
                    margin-right:8px;
                "></span>
                Homicidio
            </div>

            <div style="margin-bottom:6px;">
                <span style="
                    display:inline-block;
                    width:14px;
                    height:14px;
                    background:green;
                    border-radius:50%;
                    margin-right:8px;
                "></span>
                Narcotráfico
            </div>

            <div style="margin-bottom:6px;">
                <span style="
                    display:inline-block;
                    width:14px;
                    height:14px;
                    background:black;
                    border-radius:50%;
                    margin-right:8px;
                "></span>
                Armas
            </div>

            <div>
                <span style="
                    display:inline-block;
                    width:14px;
                    height:14px;
                    background:blue;
                    border-radius:50%;
                    margin-right:8px;
                "></span>
                Otros
            </div>

        </div>
        """
        mapa.get_root().html.add_child(folium.Element(legend_html)) 
        
    
    except Exception as e:
        print(f" Nota: No se pudo conectar a la DB local. ¿Está prendido Docker? ({e})")

    
    # --- PARTE 3: GENERACIÓN DE CAPA DE CALOR Y GUARDADO ---
    if puntos_totales:
        # HeatMap(puntos_totales, radius=70, blur=10).add_to(capa_calor)

#         HeatMap(
#     puntos_totales,
#     radius=20,        # tamaño del área de influencia
#     blur=18,          # suavizado
#     min_opacity=0.35, # evita puntos casi invisibles
#     max_zoom=12,
#     gradient={
#         0.2: "#2c7bb6",   # azul
#         0.4: "#00a6ca",
#         0.6: "#00cc66",   # verde
#         0.8: "#ffcc00",   # amarillo
#         1.0: "#d7191c"    # rojo
#     }
# ).add_to(capa_calor)
#         capa_calor.add_to(mapa)

        # HeatMap(
        #     puntos_totales,
        #     radius=70,
        #     blur=60,
        #     max_zoom=10
        # ).add_to(capa_calor)
                

        folium.LayerControl().add_to(mapa)
        
        mapa.save(salida_final)
        print(f"\n✨ PROYECTO INTEGRADO CON ÉXITO")
        print(f"📂 Archivo generado: {salida_final}")
    else:
        print("\nError: No se encontraron puntos para graficar. Revisa la DB y el CSV.")

def obtener_registros() -> list[tuple[Any, ...]]:
    query = """
        SELECT tipo_delito,
               resumen_breve,
               ST_Y(geom) AS lat,
               ST_X(geom) AS lng,
               url_fuente,
               ciudad,
               to_char(fecha_evento, 'dd/mm/yyyy') AS fecha
        FROM delitos
        WHERE geom IS NOT NULL;
    """

    with get_connection() as conexion:
        with conexion.cursor() as cursor:
            cursor.execute(query)
            registros = cursor.fetchall()

    if registros and isinstance(registros[0], dict):
        return [
            (
                reg.get("tipo_delito"),
                reg.get("resumen_breve"),
                reg.get("lat"),
                reg.get("lng"),
                reg.get("url_fuente"),
                reg.get("ciudad"),
                reg.get("fecha"),
            )
            for reg in registros
        ]

    return registros


def agregar_incidente(capa_marcadores: folium.FeatureGroup, registro: Any, puntos_calor: list[list[float]]) -> None:
    if isinstance(registro, dict):
        tipo = registro.get("tipo_delito")
        resumen = registro.get("resumen_breve")
        lat = registro.get("lat")
        lng = registro.get("lng")
        url = registro.get("url_fuente")
        ciudad = registro.get("ciudad")
        fecha = registro.get("fecha")
    else:
        tipo, resumen, lat, lng, url, ciudad, fecha = registro

    if lat is None or lng is None:
        return

    popup_html = crear_popup(tipo, resumen, ciudad, fecha, url)
    folium.Marker(
        location=[float(lat), float(lng)],
        popup=popup_html,
        tooltip=limpiar_texto(tipo),
        icon=obtener_icono(tipo),
    ).add_to(capa_marcadores)
    puntos_calor.append([float(lat), float(lng)])


def agregar_leyenda(mapa: folium.Map) -> None:
    leyenda_html = textwrap.dedent(
        """
        <div style="position: fixed; bottom: 40px; left: 40px; width: 220px; background-color: white; border-radius: 12px; padding: 14px; z-index: 9999; font-size: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.25); border: 1px solid #ddd;">
            <div style="font-weight: bold; margin-bottom: 10px; font-size: 15px; color: #2c3e50; text-align: center;">Tipos de Delito</div>
            <div style="margin-bottom: 6px;"><span style="display:inline-block; width:14px; height:14px; background:red; border-radius:50%; margin-right:8px;"></span>Robo / Asalto</div>
            <div style="margin-bottom: 6px;"><span style="display:inline-block; width:14px; height:14px; background:orange; border-radius:50%; margin-right:8px;"></span>Homicidio</div>
            <div style="margin-bottom: 6px;"><span style="display:inline-block; width:14px; height:14px; background:green; border-radius:50%; margin-right:8px;"></span>Narcotráfico</div>
            <div style="margin-bottom: 6px;"><span style="display:inline-block; width:14px; height:14px; background:black; border-radius:50%; margin-right:8px;"></span>Armas</div>
            <div><span style="display:inline-block; width:14px; height:14px; background:blue; border-radius:50%; margin-right:8px;"></span>Otros</div>
        </div>
        """
    )
    mapa.get_root().html.add_child(folium.Element(leyenda_html))


def integrar_todo_moderno() -> None:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    salida_final = os.path.join(script_dir, MAPA_SALIDA)

    mapa = folium.Map(location=UBICACION_MAPA, zoom_start=ZOOM_INICIAL, tiles=TILESET)
    capa_marcadores = folium.FeatureGroup(name="Incidentes individuales").add_to(mapa)
    capa_calor = folium.FeatureGroup(name="Mapa de calor").add_to(mapa)

    puntos_calor: list[list[float]] = []
    registros: list[tuple[Any, ...]] = []

    try:
        registros = obtener_registros()
        print(f"✅ Se encontraron {len(registros)} registros en la base de datos.")
    except Exception as error:
        print(f"⚠️ No se pudo consultar la base de datos: {error}")

    for registro in registros:
        agregar_incidente(capa_marcadores, registro, puntos_calor)

    if puntos_calor:
        HeatMap(
            puntos_calor,
            radius=18,
            blur=16,
            min_opacity=0.4,
            max_zoom=12,
            gradient={
                0.2: "#2c7bb6",
                0.4: "#00a6ca",
                0.6: "#00cc66",
                0.8: "#ffcc00",
                1.0: "#d7191c",
            },
        ).add_to(capa_calor)

    folium.LayerControl(collapsed=False).add_to(mapa)
    agregar_leyenda(mapa)
    mapa.save(salida_final)

    if puntos_calor:
        print(f"✨ Mapa generado con éxito: {salida_final}")
    else:
        print(f"⚠️ Se generó el mapa sin puntos. Revisa la base de datos o la consulta SQL.")


if __name__ == "__main__":
    integrar_todo_moderno()