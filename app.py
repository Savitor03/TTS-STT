import streamlit as st
from gtts import gTTS
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import tempfile
import os

# TTS function using gTTS (cloud-friendly)
def text_to_speech(text):
    tts = gTTS(text)
    temp_file = "temp_tts.mp3"
    tts.save(temp_file)
    return temp_file

# STT function from live recording
def record_audio(duration=5, fs=44100):
    st.info(f"Recording for {duration} seconds...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    sf.write(temp_audio.name, recording, fs)
    return temp_audio.name

def speech_to_text(audio_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_path) as source:
        audio = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            return "Couldn't understand the audio."
        except sr.RequestError:
            return "API unavailable or quota exceeded."

# Streamlit UI
st.title("Real-Time Voice ↔ Text Converter")
st.markdown("Speak or type and instantly convert between text and voice.")

mode = st.radio("Select Mode", ["Text to Speech", "Speech to Text (Live)"])

# TTS Section
if mode == "Text to Speech":
    text_input = st.text_area("Enter text to convert to voice:")
    if st.button("Generate Voice"):
        if text_input.strip():
            audio_file = text_to_speech(text_input)
            st.success("Speech generated!")
            st.audio(audio_file, format="audio/mp3")
        else:
            st.warning("Enter some text first.")

# STT Section (Live mic)
elif mode == "Speech to Text (Live)":
    duration = st.slider("Recording duration (seconds)", 3, 10, 5)
    if st.button("Record and Transcribe"):
        audio_path = record_audio(duration)
        st.success("Audio recorded!")
        st.audio(audio_path, format="audio/wav")
        with st.spinner("Transcribing..."):
            result = speech_to_text(audio_path)
            st.text_area("Transcribed Text:", value=result, height=200)
        os.remove(audio_path)
