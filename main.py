import os
import requests
import asyncio
import google.generativeai as genai
import edge_tts

# 1. إعداد Gemini API
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. توليد سيناريو كرتوني طريف
prompt = "اكتب موقفًا كرتونيًا طريفًا وقصيرًا جداً بين طفل ووالده باللغة العربية في فقرة واحدة فقط."
response = model.generate_content(prompt)
script_text = response.text.strip()
print(f"Generated Script: {script_text}")

# 3. تحويل النص إلى صوت (Voiceover)
async def generate_audio(text, output_file):
    communicate = edge_tts.Communicate(text, "ar-EG-SalmaNeural")
    await communicate.save(output_file)

audio_file = "voiceover.mp3"
asyncio.run(generate_audio(script_text, audio_file))

# 4. توليد صورة كرتونية ملائمة من Pollinations AI
image_prompt = "Cute 3D Pixar style animation of a funny child playing a prank on his dad, bright colors"
image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(image_prompt)}?width=1080&height=1920&nologo=true"

image_file = "scene.jpg"
img_data = requests.get(image_url).content
with open(image_file, 'wb') as handler:
    handler.write(img_data)

print("Audio and Image generated successfully!")
