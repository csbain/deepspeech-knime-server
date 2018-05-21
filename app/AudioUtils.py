import shutil
import sox
import webrtcvad


class AudioUtils():
    main_temp_audio_file = None
    wip_temp_audio_file = None
    main_temp_audio_16khz_file = None
    vad = None
    split_audio_files = []
    working_temp_folder = None
    temp_file_helper = None

    def __init__(self, temp_file_helper, file_bytes, file_ext):
        self.temp_file_helper = temp_file_helper
        self.vad = webrtcvad.Vad()
        self.main_temp_audio_file = self.temp_file_helper.generate_temp_filename(file_ext)
        self.wip_temp_audio_file = self.temp_file_helper.generate_temp_filename("wav")
        with open(self.main_temp_audio_file, "wb") as f_main, open(self.wip_temp_audio_file, "wb") as f_wip:
            f_main.write(file_bytes)
            f_wip.write(file_bytes)

        self.convert_audio(file_type=file_ext, samplerate=16000, n_channels=1)
        self.clean_audio()

    def generate_noise_profile(self, seconds_start=0, seconds_finish=0.5):
        tfm = sox.Transformer()
        wip_profile_file = self.temp_file_helper.generate_temp_filename()
        effect_args = ['trim', str(seconds_start), str(seconds_finish), 'noiseprof', wip_profile_file]
        tfm.build(self.wip_temp_audio_file, None, extra_args=effect_args)
        return wip_profile_file

    def convert_audio(self, file_type=None, samplerate=None, n_channels=None, bitdepth=None):
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

    def save_output_to_wav(self, path):
        shutil.copyfile(self.wip_temp_audio_file, path)
