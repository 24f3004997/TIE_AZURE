import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

class InteractionEngine:
    def __init__(self):
        # ✅ Reuses the exact same keys as your other files
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.service_region = os.getenv("AZURE_SPEECH_REGION")

    def analyze(self, audio_path):
        """
        Calculates Interaction Ratio using Azure Speech Timestamps.
        Logic: Time NOT spent transcribing speech = Interaction/Silence.
        """
        if not self.speech_key or not self.service_region:
            print("⚠️ Azure Speech Key missing. Returning default.")
            return {"interaction_ratio_percent": 30, "class_mode": "Lecture"}

        try:
            # 1. Configure Azure
            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
            speech_config.speech_recognition_language = "en-US"
            # Request detailed timing results
            speech_config.request_word_level_timestamps()
            
            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            # 2. Track Speaking Time
            total_speaking_ticks = 0
            last_end_offset = 0
            
            # Helper: 1 tick = 100 nanoseconds. 10,000,000 ticks = 1 second.
            
            done = False
            
            def handle_result(evt):
                nonlocal total_speaking_ticks, last_end_offset
                if evt.result.text:
                    # Azure gives us Duration in ticks
                    total_speaking_ticks += evt.result.duration
                    
                    # Track where the last word ended (to estimate total file length)
                    end_offset = evt.result.offset + evt.result.duration
                    if end_offset > last_end_offset:
                        last_end_offset = end_offset

            def stop_cb(evt):
                nonlocal done
                done = True

            # 3. Connect Events
            recognizer.recognized.connect(handle_result)
            recognizer.session_stopped.connect(stop_cb)
            recognizer.canceled.connect(stop_cb)

            # 4. Start Analysis
            # print(f"Processing Interaction for: {audio_path}")
            recognizer.start_continuous_recognition()
            
            while not done:
                time.sleep(0.5)

            recognizer.stop_continuous_recognition()

            # 5. Calculate Ratios
            # If total length is 0 (empty file), avoid division by zero
            if last_end_offset == 0:
                return {"interaction_ratio_percent": 0, "class_mode": "Silent"}

            # Convert ticks to seconds
            spoken_seconds = total_speaking_ticks / 10_000_000
            total_seconds = last_end_offset / 10_000_000
            
            # Interaction = Time NOT spent speaking (Silence/Discussion)
            silence_seconds = total_seconds - spoken_seconds
            interaction_ratio = int((silence_seconds / total_seconds) * 100)

            # 6. Determine Class Mode
            if interaction_ratio < 15:
                mode = "Lecture (Low Interaction)"
            elif interaction_ratio > 45:
                mode = "Discussion / Group Work"
            else:
                mode = "Interactive Lecture"

            return {
                "interaction_ratio_percent": interaction_ratio,
                "class_mode": mode
            }

        except Exception as e:
            print(f"❌ Interaction Engine Error: {e}")
            return {"interaction_ratio_percent": 0, "class_mode": "Error"}