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

mode = "default"

def note_name_from_pitch(pitch):
  rounded_pitch = round(pitch)
  note = notes[rounded_pitch % 12]
  octave = math.floor(rounded_pitch / 12)
  return f"{note}{octave}"

def start():
  button.configure(text="stop", command=stop)
  global running; running = True
  line = canvas.create_line(30, 0, 470, 0)
  window.after(1, lambda: step(line))

def step(prevLine):
  audiobuffer = stream.read(buffer_size)
  signal = np.fromstring(audiobuffer, dtype=np.float32)

  pitch = pitch_o(signal)[0]

  if mode == "tuner":
    percent = pitch - round(pitch) + 0.5
    y = percent * 400
  else:
    # y axis is from 40 to 80
    percent = 1 - ((pitch - 40) / 40)
    y = percent * 400

  canvas.delete(prevLine)
  line = canvas.create_line(30, y, 470, y)

  if pitch > 0:
    current_note_label.configure(text=note_name_from_pitch(pitch))
  else:
    current_note_label.configure(text="-")

  if running:
    window.after(1, lambda: step(line))

def stop():
  global running; running = False
  button.configure(text="start", command=start)

def clear_background_items():
  global background_items
  for line in background_items:
    canvas.delete(line)
  background_items = []

def setup_default():
  clear_background_items()
  global mode; mode = "default"
  for i in range(40, 81):
    percent = 1 - ((i - 40) / 40)
    y = percent * 400
    background_items.append(canvas.create_line(0, y, 500, y, fill="lightgrey"))
    background_items.append(canvas.create_text(20, y, text=note_name_from_pitch(i), fill="black"))

def setup_tuner():
  clear_background_items()
  global mode; mode = "tuner"
  background_items.append(canvas.create_line(0, 200, 500, 200), fill="lightgrey")

background_items = []
window = tk.Tk()

current_note_label = tk.Label(master=window, text="-")
current_note_label.pack()

canvas = tk.Canvas(master=window, width=500, height=400, relief=tk.RAISED, borderwidth=2)
canvas.pack()

button = tk.Button(master=window, text="start", command=start)
button.pack()

default_button = tk.Button(master=window, text="default", command=setup_default)
default_button.pack()

tuner_button = tk.Button(master=window, text="tuner", command=setup_tuner)
tuner_button.pack()

setup_default()

window.mainloop()

stream.stop_stream()
stream.close()
p.terminate()

