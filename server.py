import manager as manager
from flask import Flask, Response, request, render_template
from flask_socketio import SocketIO, send, emit
from engineio.payload import Payload
from threading import Thread
import fps as FPS

manager = manager.Manager('color')
app = Flask(__name__,
			static_folder="frontend",
			template_folder='frontend')

Payload.max_decode_packets = 74
app.config['SECRET_KEY'] = 'secret!'

socketio = SocketIO(app) # , logger=True

streaming = True
fps = FPS.FPS()

@app.after_request
def add_header(r):
    """
    	Deshabilita cache
    """
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    return r

def stream():
	global streaming

	while streaming:
		stringData = manager.getFrame()
		fps.update()
		yield(b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

def start():
	socketio.run(app, host='0.0.0.0')

@app.route('/video')
def video():
	return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def main():
	return render_template('./index.html')

@app.route('/config-colores')
def info():
    return render_template('./views/config-colores.html')

@app.route('/modo/<modo>', methods=['GET', 'POST'])
def cambiarModo(modo):
	global manager
	params = request.json

	dicParams = {
		'showID': params["showID"],
		'showTxt': params["showTxt"],
		'showCentroid': params["showCentroid"],
		'showBoundingRect': params["showBoundingRect"],
		'showMask': params["showMask"],
		'position': 'center',
		'drawContours': params["drawContours"],
		'measure': params["showMeasure"],
		'countItems': False
	}

	manager.setVariables(dicParams)
	manager.cambioModo(modo)
	return modo

@app.route('/start')
def startStream():
	global streaming

	fps.start()
	streaming = True
	Thread(target=stream, args=()).start()

	return 'OK'

@app.route('/stop')
def stopStream():
	global streaming
	fps.stop()
	print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
	print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
	streaming = False
	return 'OK'

@app.route('/velocidad/<velocidad>')
def velocidad(velocidad):
	global manager
	manager.moverCinta(velocidad)
	return 'OK'

@app.route('/direccion')
def direccion():
	global manager
	manager.cambiarDireccionCinta()
	return 'OK'

@app.route('/params/showID')
def showID():
	global manager
	manager.toggleShowID()
	return 'OK'

@app.route('/params/showCentroid')
def showCentroid():
	global manager
	manager.toggleShowCentroid()
	return 'OK'

@app.route('/params/drawContours')
def drawContours():
	global manager
	manager.toggleDrawContours()
	return 'OK'

@app.route('/params/showTxt')
def showTxt():
	global manager
	manager.toggleShowTxt()
	return 'OK'

@app.route('/params/showBoundingRect')
def showBoundingRect():
	global manager
	manager.toggleShowBoundingRect()
	return 'OK'

@app.route('/params/showMeasure')
def showMeasure():
	global manager
	manager.toggleShowMeasure()
	return 'OK'

@app.route('/params/showMask')
def showMask():
	global manager
	manager.toggleShowMask()
	return 'OK'

@socketio.on('getColores')
def handle_message(msg):
    emit('colores', manager.getColorRanges())

@socketio.on('setColores')
def handle_message(colores):
    manager.setColorRanges(colores)

if __name__ == '__main__':
	start()
