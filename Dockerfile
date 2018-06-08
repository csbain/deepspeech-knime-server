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
    supervisor \
 && rm -rf /var/lib/apt/lists/*

RUN pip3 --no-cache-dir install -U \
    AudioSegment \
    deepspeech==0.2.0a5 \
    enum34 \
    eyed3 \
    Flask \
    h5py \
    hmmlearn \
    ipykernel \
    librosa \
    mkl \
    numpy \
    Pillow \
    pyAudioAnalysis \
    pyclustering \
    pydub \
    pysoundfile \
    python_speech_features \
    scikit-image \
    scipy \
    setuptools \
    simplejson \
    sox \
    tensorflow==1.8.0 \
    webrtcvad \
    psutil

COPY app /app
COPY supervisord.conf /etc/supervisor/supervisord.conf


WORKDIR /etc/supervisor/conf.d
EXPOSE 5000 9001
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf"]