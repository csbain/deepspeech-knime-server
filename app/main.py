from flask import Flask, request, make_response, jsonify
from Service import Service

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac', 'aiff', 'm4a', 'm4b', 'au', 'dvf', 'gsm', 'mmf',
                          'mpc', 'ogg', 'oga', 'mogg', 'opus', 'ra', 'rm', 'raw', 'vox', 'tta', 'wma', ' webm'])
service2 = Service2()
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def throw_error_code(error_code, error_statement="error"):
    return make_response(error_statement, error_code)


@app.route('/', methods=['GET'])
def main():
    return make_response("Service Running OK", 200)


@app.route('/upload', methods=['POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return throw_error_code(400, "No File Part")
        file = request.files['file']
        if file.filename == '':
            return throw_error_code(400, "No selected file")
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            bytes = file.read()
            result = Service.process_audio_multiprocessor(bytes, ext)
            return make_response(jsonify(result), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
