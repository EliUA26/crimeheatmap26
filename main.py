import os
from flask import Flask, send_file
from backend.proyecto_heatmapp.conexiondb import get_connection
from flask import jsonify


app = Flask(__name__)


script_dir = os.path.dirname(os.path.abspath(__file__))

ruta_mapa = os.path.join(
    script_dir,
    'backend',
    'proyecto_heatmapp',
    'mapa.html'
)

def actualizar_mapa():
    print('actualizando mapa..')
    os.system('python3 backend/proyecto_heatmapp/super_integrador.py') 





def ejecutar_pipeline():
    print("generar raw scrappin")
    os.system('python3 backend/proyecto_heatmapp/genera_raw.py')
    print("Procesador IA")
    os.system('python3 backend/proyecto_heatmapp/procesador_ia.py')
    print("DB INJECTOR")
    os.system('python3 db_injector.py')
    print("Super Integrador")
    os.system('python3 backend/proyecto_heatmapp/super_integrador.py') 

@app.route('/')
def mostrar_mapa():
    if not os.path.exists(ruta_mapa):
        return "El mapa aún no ha sido generado. Por favor, ejecuta el pipeline primero."
    return send_file(ruta_mapa)

@app.route('/ejecutar')
def ejecutar():
    ejecutar_pipeline()
    return "Pipeline ejecutado. El mapa se ha actualizado."

@app.route('/actmapa')
def actmapa():
     actualizar_mapa()
     
     return "actualizando mapa.."


@app.route("/api/delitos")
def delitos():

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            tipo_delito,
            resumen_breve,
            ST_Y(geom) AS lat,
            ST_X(geom) AS lng,
            ciudad,
            url_fuente
        FROM delitos
        WHERE geom IS NOT NULL
    """)

    rows = cur.fetchall()

    data = []

    for row in rows:
        data.append({
            "tipo": row.get("tipo_delito"),
            "resumen": row.get("resumen_breve"),
            "lat": row.get("lat"),
            "lng": row.get("lng"),
            "ciudad": row.get("ciudad"),
            "url": row.get("url_fuente")
        })

    cur.close()
    conn.close()

    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
