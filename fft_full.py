import matplotlib.pyplot as plt
from scipy.io import wavfile as wav

import numpy as np
from scipy import arange

import wave as wf
rate, data = wav.read('rau4.wav')

ffss = wf.open('rau4.wav','rb')
print(ffss.getnchannels())
data_len = len(data)

f1 = arange(data_len)
fft_out = np.fft.fft(data)
f = np.fft.fftfreq(data_len,d = 1.0/rate)
plt.subplot(211)
plt.plot(f,np.abs(fft_out)) #fft
plt.subplot(212)
plt.plot(f1,data) #timp

plt.savefig('fig.png', dpi = 300)