import os
import time
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError

# تهيئة المفتاح
api_key = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=api_key)

MODELS_TO_TRY = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-1.0-pro"
]

def generate_content_with_fallback(prompt):
    for model_name in MODELS_TO_TRY:
        try:
            print(f"جاري المحاولة باستخدام الموديل: {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)
            print(f"تم التوليد بنجاح باستخدام {model_name}!")
            return response.text
        except ResourceExhausted:
            print(f"تجاوز الحصة للموديل {model_name}، جاري التجربة بالموديل التالي...")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"حدث خطأ مع {model_name}: {e}")
            continue

    raise Exception("تم تجاوز حصة جميع الموديلات المتاحة.")
