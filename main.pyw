import PySimpleGUI as sg
from TTS.api import TTS
from scipy.io.wavfile import write
import wave
import torch
import os
import pyaudio
import threading
from time import sleep
import sys

print(sys.path)

def record():
    print('record started')
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

    frames = []

    while True:
        data = stream.read(CHUNK)
        frames.append(data)
        global Recording
        if not Recording:
            break

    print('record finished')

    stream.stop_stream()
    stream.close()
    p.terminate()
    wf = wave.open(r'voice.wav', 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    

def generate(speech, inputfile):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
    tts.tts_to_file(text=speech, speaker_wav=inputfile, language="en", file_path="output.wav")

font = ('Helvetica', 12, 'bold')
sg.theme('DarkTeal')
sg.set_options(font=font)
colors = (sg.theme_background_color(), sg.theme_background_color())

voices = os.listdir('Voices')

newvoice = [[sg.Text('New Voice!',)],
            [sg.Button('Record!', disabled=False,  image_filename=(r'Textures/button.png'),button_color=(colors),border_width=0),sg.Button('Done!', disabled=True, image_filename=(r'Textures/button.png'),button_color=(colors),border_width=0)],
            [sg.Text('Please record 5-15 minutes of high quality audio! I recomend reading a chapter of a book, or naming random things around your room. Make sure that audio is clean, no background noise or other speakers present during the recording.', size=(25,0))]]

loadvoice = [[sg.Text('Load Voice!')],
             [sg.Listbox(voices, size=(25,10), key='Voices')]]

layout = [  [sg.Text('Welcome To Coqui AI Voice Generator!',)],
            [sg.Column(loadvoice, element_justification='c'),sg.Column(newvoice, element_justification='c')],
            [sg.Input('What should your voice say!', key = 'nput'),sg.Button('Generate',image_filename=(r'Textures/button.png'),button_color=(colors),border_width=0)]]

window = sg.Window('Coqui TTS GUI', layout, element_justification='c')

t1 = threading.Thread(target=record)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == 'Record!':
        window['Record!'].update(disabled=True)
        window['Done!'].update(disabled=False)
        Recording = True
        t1.start()
    if event == 'Done!':
        window['Record!'].update(disabled=False)
        window['Done!'].update(disabled=True)
        Recording = False
        t1.join()
        while True:
            Voice_name = sg.popup_get_text('Please Name Your Voice!')
            try:
                os.rename('voice.wav', rf'Voices\{Voice_name}.wav')
                break
            except:
                sg.popup_error('Invalid Name!')
        voices = os.listdir('Voices')
        window['Voices'].update(voices)
    if event == 'Generate':
        Speech = values['nput']
        Voice = values['Voices']
        if len(Voice) == 0:
            sg.popup_error('Please Select Voice From Voice List')
        else:
            Voice = rf'Voices\{Voice[0]}'
            sg.popup_no_titlebar('Render will start when you press ok,', 'This may take a while!')
            generate(Speech, Voice)
            sg.popup_ok(r'Successfully saved to "output.wav"')
window.close()