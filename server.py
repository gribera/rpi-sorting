import manager as manager
from flask import Flask, Response, render_template

manager = manager.Manager('forma')
app = Flask(__name__, template_folder='./server/')

def stream():
	while True:
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

if __name__ == '__main__':
    start()
