import scipy.io.wavfile as wav
from deepspeech.model import Model
import SharedParams
import sys
import time
from timeit import default_timer as timer

# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9


class DeepSpeechImp:
    ds = None

    def __init__(self):

        print('Loading model from file %s' % (SharedParams.DS_MODEL), file=sys.stderr)
        model_load_start = timer()
        self.ds = Model(SharedParams.DS_MODEL, N_FEATURES, N_CONTEXT, SharedParams.DS_ALPHABET, SharedParams.BEAM_WIDTH)
        model_load_end = timer() - model_load_start
        print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)

        print('Loading language model from files %s %s' % (SharedParams.DS_LANGUAGE_MODEL, SharedParams.DS_TRIE), file=sys.stderr)
        lm_load_start = timer()
        self.ds.enableDecoderWithLM(SharedParams.DS_ALPHABET, SharedParams.DS_LANGUAGE_MODEL, SharedParams.DS_TRIE,
                                    SharedParams.LM_WEIGHT, SharedParams.WORD_COUNT_WEIGHT,
                                    SharedParams.VALID_WORD_COUNT_WEIGHT)
        lm_load_end = timer() - lm_load_start
        print('Loaded language model in %0.3fs.' % (lm_load_end), file=sys.stderr)
        

        

    def process_audio(self, audio_path):
        try:
            fs, audio = wav.read(audio_path)
            return self.ds.stt(audio, fs)
        except Exception as ex:
            print(str(ex))
            return ""
