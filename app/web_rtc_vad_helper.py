import collections
import contextlib
import wave
import webrtcvad
import shared_params
from srs_segment import SRSegment
import util


def get_sr_segment_list(import_wav_path, vad_aggressiveness):
    vad = webrtcvad.Vad(vad_aggressiveness)  # agressiveness
    sample_rate = shared_params.SAMPLE_RATE

    with contextlib.closing(wave.open(import_wav_path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        pcm_data = wf.readframes(wf.getnframes())

    frames = frame_generator(30, pcm_data, sample_rate)
    frames = list(frames)
    return vad_processor(sample_rate, 30, 300, vad, frames)


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_processor(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    sr_segment_list = []
    sr_segment_count = 0
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    # We use a deque for our sliding window/ring buffer.
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    # We have two states: TRIGGERED and NOTTRIGGERED. We start in the
    # NOTTRIGGERED state.
    triggered = False

    voiced_frames = []
    for frame in frames:
        is_speech = vad.is_speech(frame.file_bytes, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            # If we're NOTTRIGGERED and more than 90% of the frames in
            # the ring buffer are voiced frames, then enter the
            # TRIGGERED state.
            if num_voiced > 0.9 * ring_buffer.maxlen:
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            # We're in the TRIGGERED state, so collect the audio data
            # and add it to the ring buffer.
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            # If more than 90% of the frames in the ring buffer are
            # unvoiced, then enter NOTTRIGGERED and yield whatever
            # audio we've collected.
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                temp_file_name, wav_duration = write_wave(b''.join([f.file_bytes for f in voiced_frames]))
                srsegment = SRSegment(sr_segment_count, frame.timestamp - wav_duration,
                                      wav_duration, temp_file_name)
                sr_segment_list.append(srsegment)
                sr_segment_count += 1
                ring_buffer.clear()
                voiced_frames = []

    # If we have any leftover voiced audio when we run out of input,
    # yield it.
    if voiced_frames:
        temp_file_name, wav_duration = write_wave(b''.join([f.file_bytes for f in voiced_frames]))
        srsegment = SRSegment(sr_segment_count, frame.timestamp - wav_duration,
                              wav_duration, temp_file_name)
        sr_segment_list.append(srsegment)
        sr_segment_count += 1
    return sr_segment_list


def write_wave(audio):
    """Writes a .wav file.
    Takes path, PCM audio data, and sample rate.
    """
    temp_filename = util.generate_temp_filename("wav")
    duration = 0
    with contextlib.closing(wave.open(temp_filename, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(shared_params.SAMPLE_RATE)
        wf.writeframes(audio)
        duration = wf.getnframes() / float(wf.getframerate())
    return temp_filename, duration


class Frame(object):
    """Represents a "frame" of audio data."""

    def __init__(self, file_bytes, timestamp, duration):
        self.file_bytes = file_bytes
        self.timestamp = timestamp
        self.duration = duration
