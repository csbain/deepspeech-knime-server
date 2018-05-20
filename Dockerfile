FROM python:3.6


RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get install locales

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

RUN apt-get install -y wget unzip cmake gcc git libcunit1-dev libudev-dev \
libleveldb-dev libssl-dev g++ curl libfreetype6-dev libpng12-dev libzmq3-dev \
wget pkg-config pkg-config python-software-properties libsndfile-dev sox libsox*

RUN pip3 --no-cache-dir install -U setuptools numpy Pillow scikit-image h5py librosa \
    AudioSegment hmmlearn Pillow simplejson eyed3 pydub scipy tensorflow mkl ipykernel deepspeech \
    pyAudioAnalysis pyclustering enum34 python_speech_features sox webrtcvad \
    pysoundfile Flask


#RUN pip3 --no-cache-dir install -U setuptools numpy Pillow scikit-image h5py librosa \
#    AudioSegment hmmlearn Pillow simplejson eyed3 pydub scipy tensorflow mkl ipykernel deepspeech \
#    pyAudioAnalysis pyclustering enum34 python_speech_features sox webrtcvad \
#    pysoundfile Flask

#
#RUN apt-get install -y wget unzip cmake gcc git libcunit1-dev libudev-dev \
#    libleveldb-dev libssl-dev g++ curl libfreetype6-dev libpng12-dev libzmq3-dev \
#    wget pkg-config python-software-properties rsync libsndfile-dev ffmpeg sox libsox*
#RUN pip3 --no-cache-dir install -U setuptools numpy Pillow scikit-image h5py librosa \
#    AudioSegment hmmlearn Pillow simplejson eyed3 pydub scipy tensorflow mkl ipykernel deepspeech \
#    pyAudioAnalysis pyclustering enum34 python_speech_features sox webrtcvad \
#    pysoundfile Flask
#
#
RUN mkdir models && cd models && \
    wget -O - https://github.com/mozilla/DeepSpeech/releases/download/v0.1.1/deepspeech-0.1.1-models.tar.gz | tar xvfz -


EXPOSE 5000
ADD . /app
WORKDIR /app
#
#
#
## Grab the checked out source
#
#
ENTRYPOINT ["python3", "main.py"]

