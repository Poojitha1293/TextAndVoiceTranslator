import streamlit as st
import sounddevice as sd # type: ignore
import wavio # type: ignore
import tempfile
from googletrans import Translator
from gtts import gTTS
import base64
import speech_recognition as sr

translator = Translator()

st.title("🌐 Text & Voice Translator App")

langs = {
    'Auto Detect': 'auto',
    'English': 'en',
    'Hindi': 'hi',
    'Telugu': 'te',
    'Tamil': 'ta',
    'French': 'fr',
    'Spanish': 'es',
    'German': 'de',
    'Italian': 'it',
    'Chinese': 'zh-cn',
    'Japanese': 'ja',
    'Arabic': 'ar',
    'Russian': 'ru'
}

source_lang = st.selectbox("📝 Source Language", list(langs.keys()))
target_lang = st.selectbox("🎯 Target Language", list(langs.keys()), index=1)

# Initialize session_state
if "recognized_text" not in st.session_state:
    st.session_state.recognized_text = ""
if "audio_file_path" not in st.session_state:
    st.session_state.audio_file_path = None

text = st.text_area("✍️ Enter text to translate", "")

st.write("🎙️ Record your voice below:")
duration = st.number_input("Recording duration (seconds)", min_value=1, max_value=20, value=5)

# Record button
if st.button("Record"):
    st.info("Recording...")
    fs = 44100
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    st.success("Recording complete!")

    # Save WAV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmpfile:
        wavio.write(tmpfile.name, recording, fs, sampwidth=2)
        st.session_state.audio_file_path = tmpfile.name
        st.audio(tmpfile.name)

    # Recognize speech
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(st.session_state.audio_file_path) as source:
            audio = recognizer.record(source)
            st.session_state.recognized_text = recognizer.recognize_google(audio)
            st.info(f"🗣️ Recognized Speech: {st.session_state.recognized_text}")
    except Exception as e:
        st.error(f"⚠️ Could not recognize speech: {e}")

# Decide final input (typed text > recorded text)
final_input = text.strip() if text.strip() else st.session_state.recognized_text

# Translate button
if st.button("🔄 Translate"):
    if final_input.strip():
        try:
            translation = translator.translate(final_input, src=langs[source_lang], dest=langs[target_lang])
            st.success("✅ Translation Successful!")
            st.text_area("📖 Translated Text:", translation.text, height=150)

            # TTS
            try:
                tts = gTTS(translation.text, lang=langs[target_lang])
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
                    tts.save(tmpfile.name)
                    with open(tmpfile.name, "rb") as f:
                        audio_bytes = f.read()
                        b64 = base64.b64encode(audio_bytes).decode()
                        st.markdown(f"""
                            <button onclick="document.getElementById('tts-audio').play()" 
                                    style="border:none; background:none; cursor:pointer; font-size:28px; vertical-align:middle;">
                                🔊
                            </button>
                            <audio id="tts-audio" controls style="width:28px; height:32px; vertical-align:middle;">
                                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                            </audio>
                        """, unsafe_allow_html=True)
            except:
                st.warning("⚠️ Text-to-Speech not available for this language.")
        except Exception as e:
            st.error(f"❌ Translation failed: {e}")
    else:
        st.warning("⚠️ Please enter text or record speech to translate.")
