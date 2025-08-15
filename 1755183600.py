import contextlib
import wave

import numpy as np

SAMPLING_RATE = 44100
BPM = 60
VOLUME = 0.5
OUTPUT_FILENAME = "canon.wav"

NOTES = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4, "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}


def get_note_frequency(note_name):
    if note_name.lower() == "rest":
        return 0
    octave = int(note_name[-1])
    pitch = note_name[:-1]
    semitones_from_a4 = NOTES[pitch] + (octave - 4) * 12
    return 440 * (2 ** (semitones_from_a4 / 12.0))


def generate_triangle_wave(frequency, duration, samp_rate):
    if frequency == 0:
        return np.zeros(int(samp_rate * duration))
    num_samples = int(samp_rate * duration)
    t = np.linspace(0, duration, num_samples, endpoint=False)
    sawtooth = (t * frequency) % 1.0 - 0.5
    triangle_wave = np.abs(sawtooth) * 4 - 1
    fade_duration = 0.01
    fade_samples = int(samp_rate * fade_duration)
    if num_samples > fade_samples * 2:
        fade_in = np.linspace(0, 1, fade_samples)
        fade_out = np.linspace(1, 0, fade_samples)
        triangle_wave[:fade_samples] *= fade_in
        triangle_wave[-fade_samples:] *= fade_out
    return triangle_wave


def create_track_data(score, beat_duration, samp_rate):
    track_audio = []
    for note, beats in score:
        frequency = get_note_frequency(note)
        duration = beats * beat_duration
        wave_data = generate_triangle_wave(frequency, duration, samp_rate)
        track_audio.append(wave_data)
    return np.concatenate(track_audio)


BEAT_DURATION = 60.0 / BPM
bass_line = [("D3", 2), ("A2", 2), ("B2", 2), ("F#2", 2), ("G2", 2), ("D2", 2), ("G2", 2), ("A2", 2)]
melody_part_1 = [("F#4", 1), ("E4", 1), ("D4", 1), ("C#4", 1), ("B3", 1), ("A3", 1), ("B3", 1), ("C#4", 1)]
melody_part_2 = [("D4", 1), ("C#4", 1), ("B3", 1), ("A3", 1), ("G3", 1), ("F#3", 1), ("G3", 1), ("A3", 1)]
arpeggios = [
    # D major
    ("F#4", 0.25),
    ("A4", 0.25),
    ("D5", 0.25),
    ("A4", 0.25),
    ("F#4", 0.25),
    ("A4", 0.25),
    ("D5", 0.25),
    ("A4", 0.25),
    # A major
    ("E4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
    ("E4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
    # B minor
    ("F#4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    ("F#4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    # F# minor
    ("F#4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
    ("F#4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
    # G major
    ("G4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    ("G4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    # D major
    ("F#4", 0.25),
    ("A4", 0.25),
    ("D5", 0.25),
    ("A4", 0.25),
    ("F#4", 0.25),
    ("A4", 0.25),
    ("D5", 0.25),
    ("A4", 0.25),
    # G major
    ("G4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    ("G4", 0.25),
    ("B4", 0.25),
    ("D5", 0.25),
    ("B4", 0.25),
    # A major
    ("E4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
    ("E4", 0.25),
    ("A4", 0.25),
    ("C#5", 0.25),
    ("A4", 0.25),
]

print("Assembling the musical parts...")
melody_phrase = melody_part_1 + melody_part_2
total_melody_phrases = 8

full_bass_score = bass_line * total_melody_phrases
voice1_score = melody_phrase * total_melody_phrases
voice2_score = [("Rest", 16 * 2)] + melody_phrase * 4 + [("Rest", 16 * 2)]
arpeggio_score = [("Rest", 16 * 2)] + arpeggios * 4 + [("Rest", 16 * 2)]

print("Generating audio waveforms...")
bass_track = create_track_data(full_bass_score, BEAT_DURATION, SAMPLING_RATE)
voice1_track = create_track_data(voice1_score, BEAT_DURATION, SAMPLING_RATE)
voice2_track = create_track_data(voice2_score, BEAT_DURATION, SAMPLING_RATE)
arpeggio_track = create_track_data(arpeggio_score, BEAT_DURATION, SAMPLING_RATE)

max_len = max(len(bass_track), len(voice1_track), len(voice2_track), len(arpeggio_track))
bass_track = np.pad(bass_track, (0, max_len - len(bass_track)))
voice1_track = np.pad(voice1_track, (0, max_len - len(voice1_track)))
voice2_track = np.pad(voice2_track, (0, max_len - len(voice2_track)))
arpeggio_track = np.pad(arpeggio_track, (0, max_len - len(arpeggio_track)))

print("Mixing tracks...")
mixed_track = bass_track * 0.4 + voice1_track * 0.3 + voice2_track * 0.3 + arpeggio_track * 0.25

max_amplitude = np.max(np.abs(mixed_track))
if max_amplitude > 0:
    mixed_track /= max_amplitude

amplitude_16bit = np.iinfo(np.int16).max
audio_data = (mixed_track * amplitude_16bit * VOLUME).astype(np.int16)

print(f"Writing to {OUTPUT_FILENAME}...")
try:
    with contextlib.closing(wave.open(OUTPUT_FILENAME, "w")) as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLING_RATE)
        f.writeframes(audio_data.tobytes())
    print(f"Successfully created '{OUTPUT_FILENAME}'.")
except Exception as e:
    print(f"Error writing WAV file: {e}")
