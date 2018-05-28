# deepspeech-knime-server [![CircleCI](https://circleci.com/gh/csbain/deepspeech-knime-server.svg?style=svg&circle-token=8279c40e3fd0f1cb7fb4628fac47c581856ffec8)](https://circleci.com/gh/csbain/deepspeech-knime-server)


This is a dockerfile to serve a [knime-deepspeech-server](https://hub.docker.com/r/csbain/deepspeech-knime-server/) on dockerhub.

# How to use this image
    
    docker pull csbain/deepspeech-knime-server:latest
    docker run csbain/deepspeech-knime-server -p 5000:5000


## Using the docker image

Inference on the model is done via http post requests, For example with the following curl command:

    curl -F "file=@/home/user1/audio.mp3" 127.0.0.1:5000/upload

## Background for this image
This project was the outcome of a Queensland University of Technology Masters project completed with an industry partner.

This docker image is intended to be used in conjunction with [KNIME](https://www.knime.com/) an open-source data analytics platform and [deepspeech-knime-workflow](https://github.com/csbain/deepspeech-knime-workflow).

The underlying technology utilised in this project consist of the following:
* Mozilla's [DeepSpeech](https://github.com/mozilla/DeepSpeech) for speech-to-text
* [OpenVokaturi](https://developers.vokaturi.com/getting-started/overview) for emotion analysis
* [py-webrtcvad](https://github.com/amikey/py-webrtcvad) for utilisation of WebRTC Voice Activity Detector (VAD)
* [Flask](http://flask.pocoo.org/) as a microframework to serve the above technologys via http
