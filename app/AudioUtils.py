import sox
import shutil
import webrtcvad


MARGIN_I = 2
MARGIN_V = 10
POWER = 2


class AudioUtils():
    # https://www.analyticsvidhya.com/blog/2017/08/audio-voice-processing-deep-learning/
    # http://eprints.maynoothuniversity.ie/4115/1/40.pdf
    # http://haythamfayek.com/2016/04/21/speech-processing-for-machine-learning.html
    # http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0144610
    # https://www.slideshare.net/mchua/sigproc-selfstudy-17323823
    # https://dsp.stackexchange.com/questions/24918/noise-reduction-on-wave-file
    # https://healthyalgorithms.com/2013/08/22/dsp-in-python-active-noise-reduction-with-pyaudio/
    # https://librosa.github.io/librosa_gallery/auto_examples/plot_vocal_separation.html
    # https://librosa.github.io/librosa/generated/librosa.core.load.html
    # https://github.com/endolith/waveform_analysis/blob/master/waveform_analysis/weighting_filters/ABC_weighting.py#L29
    # http://www.durrieu.ch/research/jstsp2010-media/pitchEval.py
    # http://www.durrieu.ch/publis/durrieuDavidRichard_musicallyMotivatedRepresentation_JSTSP2011.pdf
    # https://dsp.stackexchange.com/questions/1499/how-to-extract-vocal-part-from-stereo-audio-signal
    # http://web.science.mq.edu.au/~cassidy/comp449/html/comp449.html
    # http://home.iitk.ac.in/~rhegde/ee627_2018/picone.pdf
    # https://www.eit.lth.se/fileadmin/eit/courses/etin80/2017/reports/speech-recognition.pdf
    # https://dsp.stackexchange.com/questions/43616/pre-emphasizing-in-speech-recognition
    # http://allendowney.github.io/ThinkDSP/tutorial.html
    # http://ajaxsoundstudio.com/software/pyo/
    # https://github.com/belangeo/pyo/blob/master/examples/06-filters/06-vocoder.py
    # https://github.com/AllenDowney/ThinkDSP/blob/master/code/chap10.ipynb
    # https://github.com/AllenDowney/ThinkDSP
    # http://greenteapress.com/thinkdsp/html/index.html
    # https://hub.mybinder.org/user/allendowney-thinkdsp-idno6keg/tree

    # http://www.sigview.com/download.htm

    # https://ac.els-cdn.com/S1877705812000604/1-s2.0-S1877705812000604-main.pdf?_tid=71cede7e-e956-4b6c-8167-9e9372a6aba3&acdnat=1525179939_b9681c79e9447ab15a4e408ea25b78ee

    main_temp_audio_file = None
    wip_temp_audio_file = None
    main_temp_audio_16khz_file = None
    vad = None
    split_audio_files = []
    working_temp_folder = None
    temp_file_helper = None
    def __init__(self,temp_file_helper, file_bytes, file_ext):
        self.temp_file_helper = temp_file_helper
        self.vad = webrtcvad.Vad()
        self.main_temp_audio_file = self.temp_file_helper.generate_temp_filename(file_ext)
        self.wip_temp_audio_file = self.temp_file_helper.generate_temp_filename("wav")
        with open(self.main_temp_audio_file, "wb") as f_main, open(self.wip_temp_audio_file, "wb") as f_wip:
            f_main.write(file_bytes)
            f_wip.write(file_bytes)

        self.convert_audio(file_type=file_ext,samplerate=16000,n_channels=1)
        self.clean_audio()

    def generate_noise_profile(self,seconds_start = 0, seconds_finish = 0.5):
        tfm = sox.Transformer()
        wip_profile_file = self.temp_file_helper.generate_temp_filename()
        effect_args = ['trim', str(seconds_start), str(seconds_finish), 'noiseprof', wip_profile_file]
        tfm.build(self.wip_temp_audio_file, None, extra_args=effect_args)
        return wip_profile_file



    def convert_audio(self, file_type = None, samplerate = None, n_channels = None, bitdepth = None):
        wip_audio_file = self.temp_file_helper.generate_temp_filename("wav")
        tfm = sox.Transformer()
        tfm.set_input_format(file_type=file_type)
        tfm.convert(samplerate=samplerate, n_channels=n_channels, bitdepth=bitdepth)
        tfm.build(self.wip_temp_audio_file, wip_audio_file)
        self.wip_temp_audio_file = wip_audio_file
        return self

    def clean_audio(self):
        wip_audio_file = self.temp_file_helper.generate_temp_filename("wav")
        tfm = sox.Transformer()
        # tfm.noisered(self.generate_noise_profile(), amount=0.26)
        tfm.highpass(150)
        tfm.lowpass(6000)
        # tfm.norm(-2.0)
        tfm.build(self.wip_temp_audio_file, wip_audio_file)
        self.wip_temp_audio_file = wip_audio_file
        return self


    def get_processed_file(self):
        return self.wip_temp_audio_file


    def save_output_to_wav(self,path):
        shutil.copyfile(self.wip_temp_audio_file, path)

