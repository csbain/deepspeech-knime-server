FROM python:3.6

RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install -y locales

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install dependencies
#ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN apt-get update

RUN apt-get install -y wget tree unzip cmake gcc git libcunit1-dev libudev-dev \
libleveldb-dev libssl-dev g++ curl libfreetype6-dev libzmq3-dev \
wget pkg-config pkg-config libsndfile-dev sox libsox* tar

RUN pip3 --no-cache-dir install -U setuptools numpy Pillow scikit-image h5py librosa \
    AudioSegment hmmlearn Pillow simplejson eyed3 pydub scipy tensorflow mkl ipykernel deepspeech \
    pyAudioAnalysis pyclustering enum34 python_speech_features sox webrtcvad \
    pysoundfile Flask

COPY app /app
WORKDIR /app
RUN wget -O - https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz | tar xvfz -
RUN tree
EXPOSE 5000
ENTRYPOINT ["python3"]
CMD ["main.py"]
