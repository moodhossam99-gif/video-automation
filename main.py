import os
import requests
from gtts import gTTS
import google.generativeai as genai

# 1. إعداد Gemini API
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

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

# 4. توليد صورة كرتونية ملائمة
image_prompt = "Cute 3D animation style funny child playing a prank on his dad"
image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(image_prompt)}?width=1080&height=1920&nologo=true"

image_file = "scene.jpg"
img_data = requests.get(image_url, timeout=30).content
with open(image_file, 'wb') as handler:
    handler.write(img_data)

print("Image generated successfully!")
