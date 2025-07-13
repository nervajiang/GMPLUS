from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials
import requests

app = Flask(__name__)

# Firebase 初始化
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# Hugging Face API 設定
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
#HF_API_URL = "https://api-inference.huggingface.co/models/THUDM/chatglm3-6b"
HF_HEADERS = {"Authorization": "Bearer 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"}

#def query_huggingface(prompt):
#    payload = {"inputs": prompt}
#    response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)
#    result = response.json()
#    if isinstance(result, list) and "generated_text" in result[0]:
#        return result[0]["generated_text"].replace(prompt, "").strip()
#    return "AI 回覆錯誤，請稍後再試。"

def query_huggingface(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload)

        print("\n======= DEBUG OUTPUT =======")
        print("Status Code:", response.status_code)
        print("Raw Text Response:", response.text[:300])
        print("============================\n")

        result = response.json()  # 嘗試解析成 JSON

        # 一般格式會回傳 list，裡面有 generated_text
        if isinstance(result, list) and "generated_text" in result[0]:
            return result[0]["generated_text"].replace(prompt, "").strip()

        # 某些模型回傳 dict，例如：
        # { "generated_text": "..." }
        if isinstance(result, dict) and "generated_text" in result:
            return result["generated_text"].strip()

        return "❌ API 回傳格式錯誤。"
    
    except requests.exceptions.JSONDecodeError:
        return "❌ 無法解析 Hugging Face 回傳內容，模型可能還在加載中或權限不足。"
    except Exception as e:
        return f"❌ 發生錯誤：{str(e)}"



# 首頁路由
@app.route("/")
def index():
    return render_template("index.html")

# 穿搭建議頁面
@app.route("/fashion", methods=["GET", "POST"])
def fashion():
    if request.method == "POST":
        # 圖片處理邏輯待補
        return render_template("fashion.html", result="建議：搭配亮色外套與俐落髮型。")
    return render_template("fashion.html")

# AI 對話訓練頁面
@app.route("/talking", methods=["GET", "POST"])
def talking():
    ai_response = None
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if user_input:
            prompt = f"你是風趣的女生，現在和一個男生對話，對方說：「{user_input}」你會怎麼回應？"
            ai_response = query_huggingface(prompt)
    return render_template("talking.html", ai_response=ai_response)

# 投資理財頁面
@app.route("/finance")
def finance():
    return render_template("finance.html")

if __name__ == "__main__":
    app.run(debug=True)
