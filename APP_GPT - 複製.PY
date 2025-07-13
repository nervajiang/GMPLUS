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
   #          "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"

#HF_API_URL = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"
#HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"

HF_HEADERS = {"Authorization": "Bearer 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"}


def query_huggingface(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=30)
        print("Status Code:", response.status_code)
        print("Raw Text:", response.text[:500])  # 印出最多前500字
        response.raise_for_status()  # <--- 若 HTTP 錯誤會直接丟出 exception

        result = response.json()
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            return result[0]["generated_text"].strip()

        return "❌ API 回傳格式錯誤。"
    except requests.exceptions.HTTPError as http_err:
        return f"❌ HTTP 錯誤：{http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"❌ 請求錯誤：{req_err}"
    except Exception as e:
        return f"❌ 解析錯誤：{str(e)}"





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
           # prompt = f"你是風趣的女生，現在和一個男生對話，對方說：「{user_input}」你會怎麼回應？"
            prompt = f"You are a witty, flirty woman chatting with a man. He says: \"{user_input}\" What would you say?"

            ai_response = query_huggingface(prompt)
    return render_template("talking.html", ai_response=ai_response)

# 投資理財頁面
@app.route("/finance")
def finance():
    return render_template("finance.html")

if __name__ == "__main__":
    app.run(debug=True)
