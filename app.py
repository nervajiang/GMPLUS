from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials
from openai import OpenAI
from dotenv import load_dotenv
import os

app = Flask(__name__)

# ✅ 載入 .env 檔案
load_dotenv()

# ✅ 讀取 API key
openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Firebase 初始化
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

# ✅ OpenAI 初始化
client = OpenAI(api_key=openai_api_key)

# ✅ 呼叫 OpenAI 的函數
def query_openai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ OpenAI 回應錯誤：{str(e)}"

# ✅ 首頁路由
@app.route("/")
def index():
    return render_template("index.html")

# ✅ 穿搭建議頁面
@app.route("/fashion", methods=["GET", "POST"])
def fashion():
    if request.method == "POST":
        return render_template("fashion.html", result="建議：搭配亮色外套與俐落髮型。")
    return render_template("fashion.html")

# ✅ AI 對話訓練頁面
@app.route("/talking", methods=["GET", "POST"])
def talking():
    ai_response = None
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if user_input:
            #prompt = f"You are a Makes you feel relaxed and warm, flirty woman chatting with a man. He says: \"{user_input}\" What would you say?"
            prompt = f"你是一个让人感到温暖、放松且带点俏皮调情的女性，正在与一位男性聊天。你的回应应让他感到舒适、被重视，并被温柔地吸引。他说：\"{user_input}\" 你会如何回应？"
            ai_response = query_openai(prompt)
    return render_template("talking.html", ai_response=ai_response)

# ✅ 投資理財頁面
@app.route("/finance")
def finance():
    return render_template("finance.html")

if __name__ == "__main__":
    app.run(debug=True)
