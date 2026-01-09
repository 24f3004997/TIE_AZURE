# import os
# import time
# import azure.cognitiveservices.speech as speechsdk
# from dotenv import load_dotenv

# # Load the keys you already have
# load_dotenv()

# class ContentEngine:
#     def __init__(self):
#         # ✅ Reusing the same key you used in stream2_vocal
#         self.speech_key = os.getenv("AZURE_SPEECH_KEY")
#         self.service_region = os.getenv("AZURE_SPEECH_REGION")
        
#     def transcribe(self, audio_path):
#         """
#         Uses Azure Speech-to-Text to get the content metrics.
#         """
#         # Safety Check
#         if not self.speech_key or not self.service_region:
#             print("⚠️ Azure Speech Key missing in .env")
#             return {"transcription": "", "wpm": 0, "clarity_score": 0}

#         try:
#             # 1. Setup Configuration
#             speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
#             speech_config.speech_recognition_language = "en-US"
            
#             # 2. Setup Audio Input
#             audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))

#             # 3. Create Recognizer
#             recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

#             # 4. Continuous Transcription Helper
#             all_results = []
#             done = False

#             def handle_result(evt):
#                 if evt.result.text:
#                     all_results.append(evt.result.text)

#             def stop_cb(evt):
#                 nonlocal done
#                 done = True

#             # Connect events
#             recognizer.recognized.connect(handle_result)
#             recognizer.session_stopped.connect(stop_cb)
#             recognizer.canceled.connect(stop_cb)

#             # 5. Start Recognition
#             print(f"🎤 Transcribing content...")
#             recognizer.start_continuous_recognition()
            
#             # Wait loop (processing the whole file)
#             while not done:
#                 time.sleep(0.5)

#             recognizer.stop_continuous_recognition()

#             # 6. Calculate Metrics
#             full_text = " ".join(all_results)
#             word_count = len(full_text.split())


#             words = full_text.lower().split()
        
#         # List of encouraging/positive words for teachers
#             positive_words = [
#             "good", "great", "excellent", "amazing", "correct", 
#             "right", "perfect", "well done", "awesome", "nice", 
#             "brilliant", "exactly", "super", "keep up"]
        
#         # Count how many times these words appear
#             encouragement_count = sum(1 for w in words if w in positive_words)

#             # Estimate WPM (Assuming 1 minute chunks if duration unknown, or use file size approximation)
#             # For accurate WPM, we ideally need the exact duration from the file
#             estimated_minutes = 3 # Placeholder average
#             wpm = int(word_count / estimated_minutes) if estimated_minutes else 0

#             return {
#                 "transcription": full_text,
#                 "wpm": wpm,
#                 "clarity_score": min(100, int(len(full_text) / 5)), # Simple scoring logic
#                 "encouragement_count": encouragement_count
#                 }

#         except Exception as e:
#             print(f"❌ Transcription Error: {e}")
#             return {"transcription": "", "wpm": 0, "clarity_score": 0}
        

        
import os
import time
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

# Load the keys you already have
load_dotenv()

class ContentEngine:
    def __init__(self):
        # ✅ Reusing the same key you used in stream2_vocal
        self.speech_key = os.getenv("AZURE_SPEECH_KEY")
        self.service_region = os.getenv("AZURE_SPEECH_REGION")
    
    def count_syllables(self, word):
        """Helper to count syllables for Flesch-Kincaid formula"""
        word = word.lower()
        count = 0
        vowels = "aeiouy"
        if len(word) == 0: return 0
        if word[0] in vowels: count += 1
        for i in range(1, len(word)):
            if word[i] in vowels and word[i - 1] not in vowels:
                count += 1
        if word.endswith("e"): count -= 1
        if count == 0: count += 1
        return count
        
    def transcribe(self, audio_path):
        """
        Uses Azure Speech-to-Text to get content metrics + Complexity Analysis.
        """
        # Safety Check
        if not self.speech_key or not self.service_region:
            print("⚠️ Azure Speech Key missing in .env")
            return {"transcription": "", "wpm": 0, "clarity_score": 0}

        try:
            # 1. Setup Configuration
            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
            speech_config.speech_recognition_language = "en-US"
            
            # 2. Setup Audio Input
            audio_config = speechsdk.audio.AudioConfig(filename=str(audio_path))

            # 3. Create Recognizer
            recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

            # 4. Continuous Transcription Helper
            all_results = []
            done = False

            def handle_result(evt):
                if evt.result.text:
                    all_results.append(evt.result.text)

            def stop_cb(evt):
                nonlocal done
                done = True

            # Connect events
            recognizer.recognized.connect(handle_result)
            recognizer.session_stopped.connect(stop_cb)
            recognizer.canceled.connect(stop_cb)

            # 5. Start Recognition
            print(f"🎤 Transcribing content...")
            recognizer.start_continuous_recognition()
            
            # Wait loop (processing the whole file)
            while not done:
                time.sleep(0.5)

            recognizer.stop_continuous_recognition()

            # 6. Calculate Metrics
            full_text = " ".join(all_results)
            words = full_text.lower().split()
            word_count = len(words)

            # --- A. ENCOURAGEMENT LOGIC (Existing) ---
            

            # --- B. COGNITIVE COMPLEXITY LOGIC (New) ---
            sentences = full_text.split('.')
            # Remove empty strings from split
            sentences = [s for s in sentences if s.strip()] 
            sentence_count = len(sentences) if len(sentences) > 0 else 1
            
            if word_count > 0:
                # 1. Average Sentence Length (ASL)
                asl = word_count / sentence_count
                
                # 2. Average Syllables per Word (ASW)
                syllable_count = sum(self.count_syllables(w) for w in words)
                asw = syllable_count / word_count
                
                # 3. Flesch-Kincaid Grade Level Formula
                grade_level = (0.39 * asl) + (11.8 * asw) - 15.59
                
                # Normalize to 0-100 (Grade 12 = 100%)
                complexity_score = min(100, int((grade_level / 12) * 100))
                if complexity_score < 0: complexity_score = 10
                
                # 4. Depth Score (Unique Words Ratio)
                unique_words = len(set(words))
                depth_ratio = unique_words / word_count
                depth_score = int(depth_ratio * 100)
            else:
                complexity_score = 0
                depth_score = 0
                
            # Determine Label
            if complexity_score > 80: topic_level = "Advanced"
            elif complexity_score > 50: topic_level = "Intermediate"
            else: topic_level = "Basic"

            words = full_text.lower().split()
            fillers = ["um", "uh", "hmm", "like", "actually", "basically", "so"]
            filler_count = sum(1 for w in words if w in fillers)
            # --- C. WPM & RETURN ---
            estimated_minutes = 3 # Placeholder if duration unknown
            wpm = int(word_count / estimated_minutes) if estimated_minutes else 0

            return {
                "transcription": full_text,
                "wpm": wpm,
                "clarity_score": min(100, int(len(full_text) / 5)),
                # New Fields
                "complexity_score": complexity_score,
                "depth_score": depth_score,
                "topic_level": topic_level,
                "filler_count": filler_count
            }

        except Exception as e:
            print(f"❌ Transcription Error: {e}")
            return {"transcription": "", "wpm": 0, "clarity_score": 0}