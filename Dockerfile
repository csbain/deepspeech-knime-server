FROM ubuntu:16.04

EXPOSE 5000
ADD . /app
WORKDIR /app

RUN apt-get update
RUN apt-get install locales

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install dependencies
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:jonathonf/python-3.6
RUN apt-get update
RUN apt-get install -y build-essential python3.6 python3.6-dev python3-pip python3.6-venv \
    python3-distutils

RUN apt-get install -y wget unzip cmake gcc git libcunit1-dev libudev-dev \
    libleveldb-dev libssl-dev g++ curl libfreetype6-dev libpng12-dev libzmq3-dev \
    wget pkg-config python-software-properties rsync libsndfile-dev ffmpeg sox libsox*
RUN curl -O https://bootstrap.pypa.io/get-pip.py && python3.6 get-pip.py && rm get-pip.py
RUN pip3.6 --no-cache-dir install -U setuptools numpy Pillow scikit-image h5py librosa \
    AudioSegment hmmlearn Pillow simplejson eyed3 pydub scipy tensorflow mkl ipykernel deepspeech \
    pyAudioAnalysis pyclustering enum34 python_speech_features sox webrtcvad \
    pysoundfile Flask



# Grab the checked out source


ENTRYPOINT ["python3.6", "main.py"]

#COPY . /workdir