import os
import asyncio
import edge_tts
import google.generativeai as genai

# 1. إعداد Gemini API
API_KEY = os.getenv("API_KEY", "").strip()
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)

# اختيار الموديل المتاح
try:
    model = genai.GenerativeModel('gemini-3.6-flash')
except Exception:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = available_models[0] if available_models else 'gemini-1.5-flash'
    model = genai.GenerativeModel(model_name)

# 2. توليد سيناريو كرتوني طريف
script_prompt = "اكتب موقفًا كرتونيًا طريفًا وقصيرًا جداً بين طفل ووالده باللغة العربية في سطرين فقط."
response = model.generate_content(script_prompt)
script_text = response.text.strip()
print(f"Generated Script:\n{script_text}")

# 3. تحويل النص إلى صوت طبيعي واحترافي (Edge TTS - صوت سلمى)
VOICE = "ar-EG-SalmaNeural"  # صوت مصري طبيعي جداً ومناسب للقصص
audio_file = "voiceover.mp3"

async def generate_voice():
    communicate = edge_tts.Communicate(script_text, VOICE)
    await communicate.save(audio_file)

asyncio.run(generate_voice())
print("High-quality Voiceover generated successfully!")
