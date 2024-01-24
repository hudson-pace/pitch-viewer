import pyaudio
import numpy as np
import aubio
import math
import tkinter as tk

# initialise pyaudio
p = pyaudio.PyAudio()

# open stream
buffer_size = 1024
pyaudio_format = pyaudio.paFloat32
n_channels = 1
samplerate = 44100
stream = p.open(format=pyaudio_format,
                channels=n_channels,
                rate=samplerate,
                input=True,
                frames_per_buffer=buffer_size)

# setup pitch
tolerance = 0.8
win_s = 4096 # fft size
hop_s = buffer_size # hop size
pitch_o = aubio.pitch("default", win_s, hop_s, samplerate)
pitch_o.set_unit("midi")
pitch_o.set_tolerance(tolerance)

notes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

running = False
def start():
  button.configure(text="stop", command=stop)
  global running; running = True
  line = canvas.create_line(30, 0, 470, 0)
  window.after(1, lambda: step(line))

def step(prevLine):
  audiobuffer = stream.read(buffer_size)
  signal = np.fromstring(audiobuffer, dtype=np.float32)

  pitch = pitch_o(signal)[0]

  rounded_pitch = round(pitch)
  note = notes[rounded_pitch % 12]
  octave = math.floor(rounded_pitch / 12)

  # y axis is from 40 to 80
  percent = 1 - ((pitch - 40) / 40)
  y = percent * 400

  canvas.delete(prevLine)
  line = canvas.create_line(30, y, 470, y)

  if pitch > 0:
    print(note, octave)
  else:
    print("-")

  if running:
    window.after(1, lambda: step(line))

def stop():
  global running; running = False
  button.configure(text="start", command=start)

window = tk.Tk()
canvas = tk.Canvas(master=window, width=500, height=400)
canvas.pack()
button = tk.Button(master=window, text="start", command=start)
button.pack()
window.mainloop()

stream.stop_stream()
stream.close()
p.terminate()

