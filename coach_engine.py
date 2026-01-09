import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class CoachEngine:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠️ Google API Key missing. Coach will be offline.")
            self.active = False
        else:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.active = True
            except Exception as e:
                print(f"⚠️ Google Gemini Connection Error: {e}")
                self.active = False

    def generate_feedback(self, analysis_data, user_query):
        if not self.active:
            return "Coach is offline. Check .env file."

        # 1. Prepare Data Context
        metrics_summary = (
            f"Speech Speed (WPM): {analysis_data.get('clarity', {}).get('wpm', 0)}\n"
            f"Pitch: {analysis_data.get('vocal', {}).get('avg_pitch', 0)} Hz\n"
            f"Interaction Ratio: {analysis_data.get('interaction', {}).get('interaction_ratio_percent', 0)}%\n"
            f"Gesture Score: {analysis_data.get('video', {}).get('gesture_energy_score', 0)}\n"
            f"Eye Contact: {analysis_data.get('video', {}).get('eye_contact_score', 0)}%\n"
        )

        # 2. Strict System Prompt
        prompt = f"""
        You are an AI Instructional Coach for a teacher. 
        Your ONLY job is to analyze the provided classroom session data and answer questions about it.

        SESSION DATA:
        {metrics_summary}

        USER QUESTION:
        "{user_query}"

        Instructions:
        1. IF the user asks about their teaching, the data, or improvement tips: Answer professionally using the numbers above.
        2. IF the user asks about ANYTHING else (e.g., general knowledge, coding, jokes, politics): Refuse politely. Say: "I can only answer questions about your teaching performance and session data."
        3. Keep answers under 3 sentences.
        """

        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"AI Error: {str(e)}"
