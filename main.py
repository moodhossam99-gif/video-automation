import os
import time
import httplib2
from google import genai
from google.genai.errors import APIError

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ==========================================
# 1. إعداد وتوليد النصوص عبر Gemini
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=GEMINI_API_KEY)

MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def generate_content_with_fallback(prompt):
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
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print(f"تجاوز الحصة للموديل {model_name}، جاري الانتقال للموديل التالي...")
                time.sleep(2)
                continue
            else:
                print(f"خطأ في Gemini API: {e}")
                raise e
    raise Exception("تم تجاوز حصة جميع الموديلات المتاحة في Gemini.")


# ==========================================
# 2. إعداد الاتصال ورفع الفيديو على YouTube
# ==========================================
YOUTUBE_CLIENT_ID = os.environ.get("YOUTUBE_CLIENT_ID")
YOUTUBE_CLIENT_SECRET = os.environ.get("YOUTUBE_CLIENT_SECRET")
YOUTUBE_REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_youtube_service():
    credentials = Credentials(
        token=None,
        refresh_token=YOUTUBE_REFRESH_TOKEN,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=YOUTUBE_CLIENT_ID,
        client_secret=YOUTUBE_CLIENT_SECRET,
        scopes=SCOPES
    )
    return build("youtube", "v3", credentials=credentials)

def upload_video_to_youtube(video_path, title, description, tags=None):
    print("جاري بدء عملية الرفع على YouTube...")
    youtube = get_youtube_service()

    body = {
        "snippet": {
            "title": title[:100],  # الحد الأقصى للعنوان 100 حرف
            "description": description,
            "tags": tags or ["automation", "shorts", "ai"],
            "categoryId": "22"  # 22 = People & Blogs
        },
        "status": {
            "privacyStatus": "public",  # أو "unlisted" للتجربة
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


# ==========================================
# 3. نقطة التشغيل الرئيسية (Main Execution)
# ==========================================
if __name__ == "__main__":
    print("--- بداية تشغيل السكربت ---")

    # أ) توليد عنوان ووصف الفيديو بواسطة Gemini
    prompt = "اكتب عنواناً جذاباً ووصفاً قصيراً لفيديو تقني مشوق. اجعل السطر الأول هو العنوان فقط."
    generated_text = generate_content_with_fallback(prompt)
    
    lines = generated_text.strip().split("\n")
    video_title = lines[0].replace("#", "").strip()
    video_description = "\n".join(lines[1:]).strip() if len(lines) > 1 else video_title

    print(f"العنوان المنشأ: {video_title}")

    # ب) التأكد من وجود ملف الفيديو أو إنشائه
    video_file = "final_video.mp4"
    if not os.path.exists(video_file):
        raise FileNotFoundError(f"لم يتم العثور على ملف الفيديو: {video_file}")

    # ج) رفع الفيديو
    upload_video_to_youtube(
        video_path=video_file,
        title=video_title,
        description=video_description,
        tags=["AI", "Automation", "Tech"]
    )

    print("--- اكتملت العملية بنجاح ---")
