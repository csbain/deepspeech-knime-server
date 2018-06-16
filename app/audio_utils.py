import sox
import util

def process_audio_dsp(file_bytes, file_type):
    temp_audio_file = util.generate_temp_filename(file_type)
    with open(temp_audio_file, "wb") as f_main:
        f_main.write(file_bytes)
    wip_audio_file = util.generate_temp_filename("wav")
    tfm = sox.Transformer()
    tfm.set_input_format(file_type=file_type)
    # tfm.noisered(self.generate_noise_profile(), amount=0.26)
    tfm.highpass(150)
    tfm.lowpass(6000)
    # tfm.norm(-2.0)
    tfm.convert(samplerate=16000, n_channels=1, bitdepth=16)
    tfm.build(temp_audio_file, wip_audio_file)
    return wip_audio_file
