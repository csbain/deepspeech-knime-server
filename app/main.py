import logging
from flask import Flask, request, make_response, jsonify
import gc
import util
from multi_processor_service import MultiProcessorService
from single_threaded_service import SingleThreadedService

request_in_progress = 0

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(processName)-10s %(name)s %(levelname)-8s %(message)s')

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

@app.route('/restart', methods=['GET'])
def restart():
    util.restart_flask_server()
    return make_response("Service restarted", 200)


@app.route('/process', methods=['POST'])
def upload():
    gc.collect()
    if request.method == 'POST':
        if util.is_request_underway():
            return throw_error_code(429, "Maximum of one request is permitted at any given time.")

        if 'file' not in request.files:
            error = "No File Part"
            logging.error(error)
            return throw_error_code(400, "No File Part")
        file = request.files['file']
        if file.filename == '':
            error = "No selected file"
            logging.error(error)
            return throw_error_code(400, error)
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            file_bytes = file.read()

            multiple_processes = request.args.get('multiple_processes', default="FALSE", type=str).upper()
            if multiple_processes not in ["TRUE", "FALSE"]:
                error = "multiple_processes must either be true, false (defaults to false)"
                logging.error(error)
                return throw_error_code(400, error)
            vad_aggressiveness = request.args.get('vad_aggressiveness', default=1, type=int)
            if vad_aggressiveness not in [0, 1, 2, 3]:
                error = "vad_aggressiveness must be an integer between and including 1 and 3"
                logging.error(error)
                return throw_error_code(400, error)

            if multiple_processes == "TRUE":
                service = MultiProcessorService()
            elif multiple_processes == "FALSE":
                service = SingleThreadedService()
            result = service.process_audio(file_bytes, ext, vad_aggressiveness)
            gc.collect()
            return make_response(jsonify(result), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
