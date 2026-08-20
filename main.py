import os
from gtts import gTTS
import google.generativeai as genai

# 1. إعداد API
API_KEY = os.getenv("API_KEY", "").strip()
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)

# 2. البحث عن الموديل المتاح تلقائياً لتفادي أخطاء الأسماء
try:
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    # في حال عدم توفره يختار أول موديل يطابق الذكاء الاصطناعي
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = available_models[0] if available_models else 'gemini-1.5-flash'
    model = genai.GenerativeModel(model_name)

# 3. توليد سيناريو كرتوني طريف
prompt = "اكتب موقفًا كرتونيًا طريفًا وقصيرًا جداً بين طفل ووالده باللغة العربية في سطرين فقط."
response = model.generate_content(prompt)
script_text = response.text.strip()
print(f"Generated Script: {script_text}")

# 4. تحويل النص إلى صوت (Voiceover)
tts = gTTS(text=script_text, lang='ar')
audio_file = "voiceover.mp3"
tts.save(audio_file)
print("Audio generated successfully!")
