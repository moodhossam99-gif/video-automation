import os
import time
from google import genai
from google.genai.errors import APIError

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 1. إعداد وتوليد النصوص عبر Gemini
# ==========================================
# قائمة الموديلات المتاحة والمدعومة حالياً
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-1.5-flash-latest",
]

def generate_content_with_fallback(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("لم يتم العثور على GEMINI_API_KEY في متغيرات البيئة!")

    client = genai.Client(api_key=api_key)

    for model_name in MODELS_TO_TRY:
        try:
            print(f"جاري التوليد باستخدام الموديل: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            print("تم توليد المحتوى بنجاح!")
            return response.text
        except APIError as e:
            print(f"تنبيه من الموديل {model_name}: {e}")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"خطأ غير متوقع أثناء التوليد: {e}")
            continue
            
    raise Exception("فشلت المحاولة مع جميع الموديلات المتاحة في Gemini.")


# ==========================================
# 2. إعداد الاتصال ورفع الفيديو على YouTube
# ==========================================
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    client_id = os.environ.get("YOUTUBE_CLIENT_ID")
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET")
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN")

    if not all([client_id, client_secret, refresh_token]):
        raise ValueError("بيانات اعتماد YouTube OAuth غير مكتملة في متغيرات البيئة!")

    credentials = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES
    )
    return build("youtube", "v3", credentials=credentials)

def upload_video_to_youtube(video_path, title, description, tags=None):
    print("جاري بدء عملية الرفع على YouTube...")
    try:
        youtube = get_youtube_service()

        body = {
            "snippet": {
                "title": title[:100],
                "description": description,
                "tags": tags or ["automation", "shorts", "ai"],
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False
            }
        }

        media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"نسبة الرفع: {int(status.progress() * 100)}%")

        print(f"تم الرفع بنجاح! رابط الفيديو: https://youtu.be/{response['id']}")
        return response
    except Exception as e:
        print(f"خطأ أثناء الرفع على يوتيوب: {e}")
        raise e


# ==========================================
# 3. نقطة التشغيل الرئيسية (Main Execution)
# ==========================================
if __name__ == "__main__":
    print("--- بداية تشغيل السكربت ---")

    prompt = "اكتب عنواناً جذاباً ووصفاً قصيراً لفيديو تقني مشوق. اجعل السطر الأول هو العنوان فقط."
    generated_text = generate_content_with_fallback(prompt)
    
    lines = generated_text.strip().split("\n")
    video_title = lines[0].replace("#", "").strip()
    video_description = "\n".join(lines[1:]).strip() if len(lines) > 1 else video_title

    print(f"العنوان المنشأ: {video_title}")

    video_file = "final_video.mp4"
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"لم يتم العثور على ملف الفيديو: {video_file}")

    upload_video_to_youtube(
        video_path=video_file,
        title=video_title,
        description=video_description,
        tags=["AI", "Automation", "Tech"]
    )

    print("--- اكتملت العملية بنجاح ---")
