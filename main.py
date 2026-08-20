import os
from gtts import gTTS
import google.generativeai as genai

# 1. إعداد Gemini API
API_KEY = os.getenv("API_KEY", "").strip()
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)

# استخدام الموديل الأحدث المدعوم
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. توليد سيناريو كرتوني طريف
prompt = "اكتب موقفًا كرتونيًا طريفًا وقصيرًا جداً بين طفل ووالده باللغة العربية في سطرين فقط."
response = model.generate_content(prompt)
script_text = response.text.strip()
print(f"Generated Script: {script_text}")

# 3. تحويل النص إلى صوت (Voiceover)
tts = gTTS(text=script_text, lang='ar')
audio_file = "voiceover.mp3"
tts.save(audio_file)
print("Audio generated successfully!")
