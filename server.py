import manager as manager
from flask import Flask, Response, render_template

manager = manager.Manager('forma')
app = Flask(__name__, template_folder='./frontend/')
streaming = True

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

@app.route('/modo/<modo>')
def cambiarModo(modo):
	global manager

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

if __name__ == '__main__':
    start()
