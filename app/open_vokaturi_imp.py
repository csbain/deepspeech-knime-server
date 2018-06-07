import logging
import platform
import scipy.io.wavfile
# from vokaturi import Vokaturi

import ctypes

class Quality(ctypes.Structure):
    _fields_ = [
        ("valid", ctypes.c_int),
        ("num_frames_analyzed", ctypes.c_int),
        ("num_frames_lost", ctypes.c_int),
    ]

class EmotionProbabilities(ctypes.Structure):
    _fields_ = [
        ("neutrality", ctypes.c_double),
        ("happiness", ctypes.c_double),
        ("sadness", ctypes.c_double),
        ("anger", ctypes.c_double),
        ("fear", ctypes.c_double),
    ]

class OpenVokaturiImp:
    _library = None

    def __init__(self):
        logging.info("Loading library...")
        if platform.machine().endswith('64'):
            self._library = ctypes.CDLL("vokaturi/linux/OpenVokaturi-3-0-linux64.so")
        else:
            self._library = ctypes.CDLL("vokaturi/linux/OpenVokaturi-3-0-linux32.so")

        self._library.VokaturiVoice_create.restype = ctypes.c_void_p
        self._library.VokaturiVoice_create.argtypes = [
            ctypes.c_double,  # sample_rate
            ctypes.c_int,
        ]  # buffer_length

        self._library.VokaturiVoice_setRelativePriorProbabilities.restype = None
        self._library.VokaturiVoice_setRelativePriorProbabilities.argtypes = [
            ctypes.c_void_p,  # voice
            ctypes.POINTER(EmotionProbabilities),
        ]  # priorEmotionProbabilities

        self._library.VokaturiVoice_fill.restype = None
        self._library.VokaturiVoice_fill.argtypes = [
            ctypes.c_void_p,  # voice
            ctypes.c_int,  # num_samples
            ctypes.POINTER(ctypes.c_double),
        ]  # samples

        self._library.VokaturiVoice_extract.restype = None
        self._library.VokaturiVoice_extract.argtypes = [
            ctypes.c_void_p,  # voice
            ctypes.POINTER(Quality),  # quality
            ctypes.POINTER(EmotionProbabilities),
        ]  # emotionProbabilities

        self._library.VokaturiVoice_reset.restype = None
        self._library.VokaturiVoice_reset.argtypes = [ctypes.c_void_p]  # voice

        self._library.VokaturiVoice_destroy.restype = None
        self._library.VokaturiVoice_destroy.argtypes = [ctypes.c_void_p]  # voice

        self._library.Vokaturi_versionAndLicense.restype = ctypes.c_char_p
        self._library.Vokaturi_versionAndLicense.argtypes = []

    def versionAndLicense(self):
        return self._library.Vokaturi_versionAndLicense().decode("UTF-8")

    def SampleArrayC(self,size):
        return (ctypes.c_double * size)()

    def setRelativePriorProbabilities(self, priorEmotionProbabilities):
        self._library.VokaturiVoice_setRelativePriorProbabilities(
            self._voice, priorEmotionProbabilities
        )

    def fill(self, num_samples, samples):
        self._library.VokaturiVoice_fill(self._voice, num_samples, samples)

    def extract(self, quality, emotionProbabilities):
        self._library.VokaturiVoice_extract(self._voice, quality, emotionProbabilities)

    def reset(self):
        self._library.VokaturiVoice_reset(self._voice)

    def analyse_audio(self, file_name):
        (sample_rate, samples) = scipy.io.wavfile.read(file_name)
        buffer_length = len(samples)
        c_buffer = self.SampleArrayC(buffer_length)
        if samples.ndim == 1:  # mono
            c_buffer[:] = samples[:] / 32768.0
        else:  # stereo
            c_buffer[:] = 0.5 * (samples[:, 0] + 0.0 + samples[:, 1]) / 32768.0

        self._voice = self._library.VokaturiVoice_create(sample_rate, buffer_length)
        self._voice.fill(buffer_length, c_buffer)
        quality = Quality()
        emotion_probabilities = EmotionProbabilities()
        self._voice.extract(quality, emotion_probabilities)
        emotion = {
            "neutrality": emotion_probabilities.neutrality,
            "happiness": emotion_probabilities.happiness,
            "sadness": emotion_probabilities.sadness,
            "anger": emotion_probabilities.anger,
            "fear": emotion_probabilities.fear
        }
        self.reset()
        self._voice.destroy()
        del self._voice
        del self._library
        return emotion

