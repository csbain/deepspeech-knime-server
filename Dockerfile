FROM python:3.6

RUN apt-get update && apt-get install -y \
    apt-utils \
    curl \
    g++ \
    gcc \
    git \
    libcunit1-dev \
    libfreetype6-dev \
    libleveldb-dev \
    libsndfile-dev \
    libsox* \
    libssl-dev \
    libudev-dev \
    libzmq3-dev \
    pkg-config \
    software-properties-common \
    sox \
    tar \
    unzip \
    wget \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install -U \
    AudioSegment
    deepspeech
    enum34
    eyed3
    Flask
    h5py
    hmmlearn
    ipykernel
    librosa
    mkl
    numpy
    Pillow
    pyAudioAnalysis
    pyclustering
    pydub
    pysoundfile
    python_speech_features
    scikit-image
    scipy
    setuptools
    simplejson
    sox
    tensorflow
    webrtcvad

COPY app /app
WORKDIR /app
#RUN wget -O - https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz | tar xvfz -
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["main.py"]
