# import os
# import azure.cognitiveservices.speech as speechsdk
# from dotenv import load_dotenv

# load_dotenv()

# class AzureSpeechEngine:
#     def __init__(self):
#         self.key = os.getenv("AZURE_SPEECH_KEY")
#         self.region = os.getenv("AZURE_SPEECH_REGION")
#         self.active = self.key and self.region

#     def analyze(self, audio_path):
#         if not self.active:
#             # Fallback mock data if keys are missing
#             return {"avg_pitch": 120, "delivery_status": "Azure Keys Missing"}

#         try:
#             # 1. Configure Azure Speech
#             speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
#             audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))

#             # 2. Use Pronunciation Assessment (The "Cheat Code" feature)
#             # This automatically grades fluency, prosody, and completeness.
#             pronunciation_config = speechsdk.PronunciationAssessmentConfig(
#                 reference_text="", # Empty string means "Open Grading" (assess whatever is said)
#                 grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
#                 granularity=speechsdk.PronunciationAssessmentGranularity.FullText,
#                 enable_miscue=True
#             )
#             pronunciation_config.enable_prosody_assessment()

#             # 3. Create Recognizer
#             recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
#             pronunciation_config.apply_to(recognizer)

#             # 4. Run Analysis (One-shot for simplicity)
#             result = recognizer.recognize_once()

#             # 5. Extract Scores
#             if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#                 pron_result = speechsdk.PronunciationAssessmentResult(result)
#                 return {
#                     "avg_pitch": int(pron_result.prosody_score), # Using prosody as a proxy for pitch quality
#                     "delivery_status": "Professional (Azure Verified)",
#                     "fluency_score": pron_result.fluency_score,
#                     "completeness_score": pron_result.completeness_score
#                 }
#             else:
#                 return {"avg_pitch": 0, "delivery_status": "No Speech Detected"}

#         except Exception as e:
#             print(f"Azure Speech Error: {e}")
#             return {"avg_pitch": 0, "delivery_status": "Error"}


import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

class AzureSpeechEngine:
    def __init__(self):
        self.key = os.getenv("AZURE_SPEECH_KEY")
        self.region = os.getenv("AZURE_SPEECH_REGION")
        self.active = self.key and self.region

    def analyze(self, audio_path):
        """
        Analyzes audio for Pitch, Fluency, and Emotional Tone using Azure.
        """
        # 1. Fallback if keys are missing
        if not self.active:
            return {
                "avg_pitch": 120, 
                "delivery_status": "Keys Missing",
                "emotion_detected": "Neutral",
                "emotional_intensity": 50
            }

        try:
            # 2. Configure Azure Speech
            speech_config = speechsdk.SpeechConfig(subscription=self.key, region=self.region)
            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))

            # 3. Setup Pronunciation Assessment
            # We use this to get 'Prosody' (Expressiveness) and 'Fluency'
            pronunciation_config = speechsdk.PronunciationAssessmentConfig(
                reference_text="", # Empty = Open grading
                grading_system=speechsdk.PronunciationAssessmentGradingSystem.HundredMark,
                granularity=speechsdk.PronunciationAssessmentGranularity.FullText,
                enable_miscue=True
            )
            pronunciation_config.enable_prosody_assessment()

            # 4. Create Recognizer & Apply Config
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
            pronunciation_config.apply_to(recognizer)

            # 5. Run Analysis (One-shot)
            result = recognizer.recognize_once()

            # 6. Extract & Calculate Scores
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                pron_result = speechsdk.PronunciationAssessmentResult(result)
                
                # Metrics from Azure
                prosody = pron_result.prosody_score  # Measures expressiveness/intonation
                fluency = pron_result.fluency_score  # Measures smoothness
                
                # --- NEW: EMOTION MAPPING LOGIC ---
                # We derive emotion from Prosody (Expressiveness) + Fluency
                
                if prosody > 90:
                    emotion = "Passionate"
                    intensity = int(prosody)
                elif prosody > 80 and fluency > 80:
                    emotion = "Confident"
                    intensity = int(prosody)
                elif prosody > 70:
                    emotion = "Professional"
                    intensity = int(prosody)
                elif prosody < 60:
                    emotion = "Monotone"
                    intensity = int(prosody)
                else:
                    emotion = "Neutral"
                    intensity = int(prosody)
                # ----------------------------------

                return {
                    "avg_pitch": int(prosody), # Using prosody as pitch quality score (0-100)
                    "delivery_status": "Professional (Azure Verified)",
                    "fluency_score": fluency,
                    "completeness_score": pron_result.completeness_score,
                    # New Fields for your Card
                    "emotion_detected": emotion,
                    "emotional_intensity": intensity
                }
            
            elif result.reason == speechsdk.ResultReason.NoMatch:
                return {
                    "avg_pitch": 0, "delivery_status": "Silence", 
                    "emotion_detected": "Silent", "emotional_intensity": 0
                }
            else:
                return {
                    "avg_pitch": 0, "delivery_status": "Processing Error",
                    "emotion_detected": "Unknown", "emotional_intensity": 0
                }

        except Exception as e:
            print(f"❌ Azure Speech Error: {e}")
            return {
                "avg_pitch": 0, "delivery_status": "Error",
                "emotion_detected": "Error", "emotional_intensity": 0
            }