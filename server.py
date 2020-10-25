import manager as manager
from flask import Flask, Response, request, render_template

manager = manager.Manager('color')
app = Flask(__name__,
			static_folder="frontend",
			template_folder='frontend')
streaming = True

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, public, max-age=0'
    r.headers['Pragma'] = 'no-cache'
    r.headers['Expires'] = '0'
    return r

def stream():
	global streaming

	while streaming:
		stringData = manager.getFrame()
		yield(b'--frame\r\n'b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

def start():
	app.run(host='0.0.0.0')

@app.route('/video')
def video():
	return Response(stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def main():
	return render_template('./index.html')

@app.route('/modo/<modo>', methods=['GET', 'POST'])
def cambiarModo(modo):
	global manager
	params = request.json
	manager.setVariables(showID=params["showID"],
						 showCentroid=params["showCentroid"],
						 drawContours=params["drawContours"],
						 showForma=params["showForma"],
						 showBoundingRect=params["showBoundingRect"],
						 measure=params["showMeasure"])
	manager.cambioModo(modo)
	return modo

@app.route('/start')
def startStream():
	global streaming
	streaming = True
	stream()

	return 'OK'

@app.route('/stop')
def stopStream():
	global streaming
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

@app.route('/params/showForma')
def showForma():
	global manager
	manager.toggleShowForma()
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

if __name__ == '__main__':
	start()
