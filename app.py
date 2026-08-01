import streamlit as st
import pandas as pd
import datetime
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os
import subprocess
import json

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="Gate Vehicle Logger", layout="centered")

st.title("🚗 Gate Vehicle Logging System")
st.write("Voice-enabled vehicle entry logging (15 sec recording)")

# =========================
# SESSION STORAGE
# =========================
if "log" not in st.session_state:
    st.session_state.log = []

# =========================
# AUDIO TRANSCRIPTION
# =========================
def transcribe_audio(audio_bytes):
    recognizer = sr.Recognizer()

    try:
        # Save audio as webm
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(audio_bytes)
            webm_path = temp_audio.name

        # Convert to WAV
        sound = AudioSegment.from_file(webm_path)
        wav_path = webm_path.replace(".webm", ".wav")
        sound.export(wav_path, format="wav")

        # Transcribe
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Cleanup
        os.remove(webm_path)
        os.remove(wav_path)

        return text

    except Exception as e:
        return f"ERROR: {e}"

# =========================
# OLLAMA EXTRACTION
# =========================
def extract_vehicle_data(text):
    prompt = f"""
Extract the following from the sentence:
Plate Number, Private/Public, Car Colour, Car Model.

Return ONLY JSON in this format:
{{
  "plate_number": "",
  "type": "",
  "color": "",
  "model": ""
}}

Sentence: {text}
"""

    try:
        result = subprocess.run(
            ["ollama", "run", "llama3.2:1b"],
            input=prompt.encode(),
            stdout=subprocess.PIPE
        )

        output = result.stdout.decode()

        # Extract JSON safely
        start = output.find("{")
        end = output.rfind("}") + 1
        json_str = output[start:end]

        data = json.loads(json_str)

        return data

    except Exception:
        return {
            "plate_number": "",
            "type": "",
            "color": "",
            "model": ""
        }

# =========================
# VOICE INPUT SECTION
# =========================
st.subheader("🎤 Voice Input (15 seconds)")

audio_file = st.audio_input("Record vehicle details")

if audio_file is not None:
    st.audio(audio_file)

    if st.button("🔍 Transcribe & Extract"):
        with st.spinner("Processing..."):

            # ✅ FIX: Convert UploadedFile → bytes
            audio_bytes = audio_file.read()

            text = transcribe_audio(audio_bytes)

            if "ERROR" in text:
                st.error(text)
            else:
                st.success(f"Recognized: {text}")

                data = extract_vehicle_data(text)
                st.session_state.current = data

# =========================
# MANUAL / CONFIRMATION FORM
# =========================
st.subheader("📝 Confirm Vehicle Details")

data = st.session_state.get("current", {
    "plate_number": "",
    "type": "",
    "color": "",
    "model": ""
})

plate = st.text_input("Plate Number", value=data.get("plate_number", ""))
vehicle_type = st.selectbox(
    "Private / Public",
    ["Private", "Public"],
    index=0 if data.get("type", "").lower() != "public" else 1
)
color = st.text_input("Car Colour", value=data.get("color", ""))
model = st.text_input("Car Model", value=data.get("model", ""))

# =========================
# ACTION BUTTONS
# =========================
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Confirm Entry"):
        entry = {
            "Time In": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Plate Number": plate,
            "Type": vehicle_type,
            "Color": color,
            "Model": model,
            "Checked Out": "No"
        }

        st.session_state.log.append(entry)
        st.success("Vehicle logged successfully!")

with col2:
    if st.button("🧹 Clear Form"):
        st.session_state.current = {
            "plate_number": "",
            "type": "",
            "color": "",
            "model": ""
        }
        st.rerun()

# =========================
# VEHICLE LOG TABLE
# =========================
st.subheader("📋 Vehicle Log")

if len(st.session_state.log) > 0:
    df = pd.DataFrame(st.session_state.log)
    st.dataframe(df, use_container_width=True)

    # =========================
    # CHECKOUT SECTION
    # =========================
    st.subheader("🚪 Checkout Vehicle")

    plates = df[df["Checked Out"] == "No"]["Plate Number"].tolist()

    if plates:
        selected_plate = st.selectbox("Select Plate to Checkout", plates)

        if st.button("🚗 Confirm Checkout"):
            for item in st.session_state.log:
                if item["Plate Number"] == selected_plate:
                    item["Checked Out"] = "Yes"
                    item["Time Out"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            st.success("Vehicle checked out successfully!")
            st.rerun()
    else:
        st.info("No vehicles currently inside.")

else:
    st.info("No vehicles logged yet.")