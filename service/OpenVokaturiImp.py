from service.lib.vokaturi import Vokaturi
import scipy.io.wavfile


class OpenVokaturiImp():
    def __init__(self):
        print("Loading library...")
        Vokaturi.load("lib/vokaturi/linux/OpenVokaturi-3-0-linux64.so")
        print("Analyzed by: %s" % Vokaturi.versionAndLicense())

    def analyse_audio(self, file_name):
        (sample_rate, samples) = scipy.io.wavfile.read(file_name)
        buffer_length = len(samples)
        c_buffer = Vokaturi.SampleArrayC(buffer_length)
        if samples.ndim == 1:  # mono
            c_buffer[:] = samples[:] / 32768.0
        else:  # stereo
            c_buffer[:] = 0.5 * (samples[:, 0] + 0.0 + samples[:, 1]) / 32768.0
        voice = Vokaturi.Voice(sample_rate, buffer_length)
        voice.fill(buffer_length, c_buffer)
        quality = Vokaturi.Quality()
        emotionProbabilities = Vokaturi.EmotionProbabilities()
        voice.extract(quality, emotionProbabilities)
        emotion = {
            "neutrality": emotionProbabilities.neutrality,
            "happiness": emotionProbabilities.happiness,
            "sadness": emotionProbabilities.sadness,
            "anger": emotionProbabilities.anger,
            "fear": emotionProbabilities.fear
        }
        voice.destroy()

        return emotion
