import os
import time
from google import genai
from google.genai.errors import APIError

# جلب المفتاح من GitHub Secrets
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# قائمة الموديلات المتاحة للتنقل بينها في حال امتلاء الحصة
MODELS_TO_TRY = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro"
]

def generate_content_with_fallback(prompt):
    for model_name in MODELS_TO_TRY:
        try:
            print(f"جاري المحاولة باستخدام الموديل: {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            print(f"تم التوليد بنجاح باستخدام {model_name}!")
            return response.text
        
        except APIError as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print(f"تجاوز الحصة للموديل {model_name}، جاري التجربة بالموديل التالي...")
                time.sleep(2)  # انتظار بسيط قبل التجربة التالية
                continue
            else:
                print(f"حدث خطأ غير متعلق بالحصة: {e}")
                raise e

    raise Exception("تم تجاوز حصة جميع الموديلات المتاحة، يرجى الانتظار قليلاً أو استبدال GEMINI_API_KEY.")

# مثال للاستخدام داخل السكربت الخاص بك:
if __name__ == "__main__":
    my_prompt = "اكتب عنواناً وصفياً مميزاً لفيديو يوتيوب عن التكنولوجيا"
    result = generate_content_with_fallback(my_prompt)
    print("النتيجة:", result)
