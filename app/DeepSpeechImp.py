from deepspeech.model import Model
import scipy.io.wavfile as wav


DS_MODEL_BASE = '/app/models/0.1.1/'

DS_MODEL = DS_MODEL_BASE + 'output_graph.pb'
DS_ALPHABET = DS_MODEL_BASE + 'alphabet.txt'
DS_TRIE = DS_MODEL_BASE + 'trie'
DS_LANGUAGE_MODEL = DS_MODEL_BASE + 'lm.binary'

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.25

# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
WORD_COUNT_WEIGHT = 1.00

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 1.00


# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9


class DeepSpeechImp():
    # https://progur.com/2018/02/how-to-use-mozilla-deepspeech-tutorial.html
    ds = None
    def __init__(self):

        self.ds = Model(DS_MODEL, N_FEATURES, N_CONTEXT, DS_ALPHABET, BEAM_WIDTH)

        self.ds.enableDecoderWithLM(DS_ALPHABET, DS_LANGUAGE_MODEL, DS_TRIE, LM_WEIGHT,
                               WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)

    def process_audio(self, audio_path):
        try:
            fs, audio = wav.read(audio_path)
            return self.ds.stt(audio, fs)
        except Exception:
            return ""

