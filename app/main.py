import logging
from flask import Flask, request, make_response, jsonify
import gc
import util
from asr_service import ASRService
import multiprocessing
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

            processes = request.args.get('processes', default="MAX", type=str).upper()
            cpu_count = multiprocessing.cpu_count()
            if util.is_int(processes):
                print("assigning "+processes+" processes")
                processes = int(processes)

                if processes > cpu_count:
                    return throw_error_code(400, "Process count must not exceed cpu count of "+ str(cpu_count) + \
                                            " not using the processes argument or assigning it 'MAX' will use the " +\
                                            "maximum processes available")
            elif processes.upper() == "MAX":
                processes = cpu_count
            else:
                return throw_error_code(400, "Invalid value for arg 'processes'")


            vad_aggressiveness = request.args.get('vad_aggressiveness', default=1, type=int)
            if vad_aggressiveness not in [0, 1, 2, 3]:
                error = "vad_aggressiveness must be an integer between and including 1 and 3"
                logging.error(error)
                return throw_error_code(400, error)
            service = ASRService()
            result = service.process_audio(file_bytes, ext, vad_aggressiveness, processes)
            gc.collect()
            return make_response(jsonify(result), 200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=False)
