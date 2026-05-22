import os
from flask import Flask, send_file


app = Flask(__name__)


ruta_mapa = 'backend/proyecto_heatmapp/MAPA_FINAL_ENTREGA.html'


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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)



   

