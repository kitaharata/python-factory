import numpy as np
from scipy.io.wavfile import write

samplerate = 44100
frequency = 110
duration = 1

t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
amplitude = np.iinfo(np.int16).max
data = amplitude * np.sin(2 * np.pi * frequency * t)

write("sin.wav", samplerate, data.astype(np.int16))
