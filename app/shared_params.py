SAMPLE_RATE = 16000  # SR for DeepSpeech and VAD (Deepspeech was trained on 16000 training data.

DS_MODEL_BASE = "models/"

DS_MODEL = DS_MODEL_BASE + "output_graph.pbmm"
DS_ALPHABET = DS_MODEL_BASE + "alphabet.txt"
DS_TRIE = DS_MODEL_BASE + "trie"
DS_LANGUAGE_MODEL = DS_MODEL_BASE + "lm.binary"

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.75

# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
WORD_COUNT_WEIGHT = 1.00

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 1.00

DEFAULT_METRICS_LOG_FILE = "metrics.log"
