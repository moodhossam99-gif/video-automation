import os
import asyncio
import requests
import edge_tts
import google.generativeai as genai

# استدعاء MoviePy بشكل متوافق مع كافة الإصدارات
try:
    from moviepy.editor import AudioFileClip, ImageClip
except ImportError:
    from moviepy.audio.io.AudioFileClip import AudioFileClip
    from moviepy.video.VideoClip import ImageClip

# 1. إعداد Gemini API
API_KEY = os.getenv("API_KEY", "").strip()
if not API_KEY:
    raise ValueError("API_KEY is missing!")

genai.configure(api_key=API_KEY)

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception:
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    model_name = available_models[0] if available_models else 'gemini-1.5-flash'
    model = genai.GenerativeModel(model_name)

# 2. توليد سيناريو كرتوني طريف
script_prompt = "اكتب موقفًا كرتونيًا طريفًا وقصيرًا جداً بين طفل ووالده باللغة العربية في سطرين فقط."
response = model.generate_content(script_prompt)
script_text = response.text.strip()
print(f"Generated Script:\n{script_text}")

# 3. تحويل النص إلى صوت (Edge TTS)
VOICE = "ar-EG-SalmaNeural"
audio_file = "voiceover.mp3"

async def generate_voice():
    communicate = edge_tts.Communicate(script_text, VOICE)
    await communicate.save(audio_file)

asyncio.run(generate_voice())
print("Voiceover generated successfully!")

# 4. توليد وصف الصورة بالذكاء الاصطناعي
image_prompt_req = f"Write a short, detailed image prompt in English for a 3D Pixar style cartoon scene representing this story: '{script_text}'. Keep it under 20 words."
image_prompt_res = model.generate_content(image_prompt_req)
clean_image_prompt = image_prompt_res.text.strip().replace('\n', ' ')

# 5. جلب الصورة الرأسية (1080x1920)
image_url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(clean_image_prompt)}?width=1080&height=1920&nologo=true"
image_file = "scene.jpg"

try:
    img_data = requests.get(image_url, timeout=30).content
    with open(image_file, 'wb') as handler:
        handler.write(img_data)
    print("Image generated successfully!")
except Exception as e:
    print(f"Failed to fetch image: {e}")

# 6. دمج الصوت والصورة لإنتاج فيديو final_video.mp4
try:
    audio_clip = AudioFileClip(audio_file)
    video_clip = ImageClip(image_file).set_duration(audio_clip.duration)
    final_clip = video_clip.set_audio(audio_clip)

    output_video = "final_video.mp4"
    final_clip.write_videofile(output_video, fps=24, codec="libx264", audio_codec="aac")
    print("Final MP4 Video created successfully!")
except Exception as e:
    print(f"Video creation failed: {e}")
