import json
import psycopg2
import os

def inyectar_datos():
    # Configuración (Igual a la de tus otros archivos)
    conn = psycopg2.connect(
        host="postgis.happypond-0857f03e.eastus.azurecontainerapps.io",
        database="crime_heatmap",
        user="adminua",
        password="password123",
        port="5432"
    )
    cur = conn.cursor()

    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(BASE_DIR, 'backend', 'data/noticias_mapeadas.json')

        with open(path, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        print(f"Subiendo {len(datos)} registros a la base de datos...")

        for item in datos:
            cur.execute("""
                INSERT INTO delitos (tipo_delito, fecha_evento, gravedad, ubicacion_texto, barrio, ciudad, resumen_breve, geom, url_fuente)
                VALUES (%s, %s, %s, %s, %s, %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
                ON CONFLICT (url_fuente) DO NOTHING;
            """, (
                item['tipo_delito'], item['fecha_evento'], item['gravedad'],
                item['ubicacion_texto'], item['barrio'], item['ciudad'],
                item['resumen_breve'], item['lng'], item['lat'], item['url_fuente']
            ))

        conn.commit()
        print("✅ Inyección completada exitosamente.")
    except Exception as e:
        print(f"❌ Error al inyectar datos: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    inyectar_datos()