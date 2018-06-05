from flask import Flask, request, make_response, jsonify
from MultiProcessorService import MultiProcessorService
from SingleThreadedService import SingleThreadedService

app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['wav', 'mp3', 'flac', 'aiff', 'm4a', 'm4b', 'au', 'dvf', 'gsm', 'mmf',
                          'mpc', 'ogg', 'oga', 'mogg', 'opus', 'ra', 'rm', 'raw', 'vox', 'tta', 'wma', ' webm'])

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

            multiple_processes = request.args.get('multiple_processes', default = "FALSE", type = str)
            if multiple_processes.upper() not in ["TRUE", "FALSE"]:
                return throw_error_code(400, "multiple_processes must either be true, false (defaults to false)")
            vad_aggressiveness = request.args.get('vad_aggressiveness', default = 1, type = int)
            if vad_aggressiveness not in [1,2,3]:
                return throw_error_code(400, "vad_aggressiveness must be an integer between and including 1 and 3")

            if multiple_processes.upper() == "TRUE":
                service = MultiProcessorService()
                result = service.process_audio(bytes, ext, vad_aggressiveness)
            else:
                service = SingleThreadedService()
                result = service.process_audio(bytes, ext, vad_aggressiveness)

            # result = service.process_audio_singlethreaded(bytes, ext)

            return make_response(jsonify(result), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
