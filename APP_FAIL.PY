from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials
import requests
import json # 引入 json 模組來解析可能的錯誤訊息

app = Flask(__name__)

# Firebase 初始化
# 確保 'firebase_config.json' 檔案存在於 app.py 的同層目錄中
try:
    cred = credentials.Certificate("firebase_config.json")
    firebase_admin.initialize_app(cred)
    print("Firebase initialized successfully!")
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    # 在生產環境中，這裡可以選擇記錄錯誤或退出應用程式
    # 或者提供一個友善的錯誤頁面
    pass # 為了讓應用程式即使 Firebase 初始化失敗也能啟動，暫時 pass

# Hugging Face API 設定
 #HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3"
 HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
# 請確保您的 HF_TOKEN 是正確且有效的
HF_HEADERS = {"Authorization": "Bearer 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"}

def query_huggingface(prompt):
    payload = {"inputs": prompt}
    try:
        response = requests.post(HF_API_URL, headers=HF_HEADERS, json=payload, timeout=60) # 增加 timeout
        print(f"Hugging Face API Status Code: {response.status_code}")
        print(f"Hugging Face API Raw Response Text (first 500 chars): {response.text[:500]}")

        # 檢查 HTTP 狀態碼
        response.raise_for_status()

        # 解析 JSON 回應
        try:
            result = response.json()
        except json.JSONDecodeError:
            print(f"Failed to decode JSON: {response.text}")
            return "❌ API 回傳內容不是有效的 JSON。"

        # 處理 Mistral-7B-Instruct-v0.3 模型可能的回應格式
        # 這個模型通常會將完整的 prompt 也包含在 generated_text 中
        # 我們需要從中提取實際的 AI 回應部分
        if isinstance(result, list) and len(result) > 0 and "generated_text" in result[0]:
            full_text = result[0]["generated_text"].strip()
            # 找到 prompt 結束的位置，提取其後的內容
            # 注意：Mistral Instruction 模型通常會在 prompt 後直接跟著 AI 的回應
            # 所以可以嘗試找到 prompt 的精確結尾，並取其之後的文本
            # 由於我們在 prompt 中包含了 `You are a witty, flirty woman chatting with a man. He says: "{user_input}" What would you say?`
            # 模型通常會在這個問題之後直接給出答案
            # 尋找 prompt 的結尾，並提取其後的部分
            # 更精確的方法是尋找預期的人工智能回應前綴（如果有）
            # 或者假設模型會直接從 prompt 結束的地方開始生成回應
            
            # 對於 Instruction-tuned 模型，它會完整回覆 prompt + response
            # 嘗試移除掉 prompt 部分來提取 AI 的實際回應
            # 我們傳入的 prompt 是 f"You are a witty, flirty woman chatting with a man. He says: \"{user_input}\" What would you say?"
            # 模型可能會在前面加上 "Sure, here's my response: " 或直接從後面開始生成
            
            # 最常見的做法是找到 prompt 的最後一句，並從那裡開始切
            # 或者使用更複雜的文本解析來判斷
            
            # 這裡採用一個簡化的策略，假設模型的生成通常會從提示的結尾開始
            # 但這可能不適用於所有情況，需要根據實際模型行為微調
            
            # 更穩健的方法是檢查模型行為並根據模型前綴來分割
            # 例如，如果模型回應是 "You are...say?\nAI: Blah blah", 則找 "AI:"
            
            # 目前的 Mistral 模型通常直接在 prompt 之後生成
            # 讓我們嘗試移除 prompt 本身
            if full_text.startswith(prompt):
                ai_response_text = full_text[len(prompt):].strip()
                return ai_response_text
            else:
                # 如果模型回傳的文本不以 prompt 開頭，直接回傳整個生成文本
                # 這可能是模型行為的差異，或 prompt 處理方式需調整
                return full_text
        elif isinstance(result, dict) and "error" in result:
            # 處理 Hugging Face API 回傳的錯誤訊息，例如模型加載中
            error_msg = result.get("error", "未知錯誤")
            if "is currently loading" in error_msg:
                return "❌ 模型正在加載中，請稍候再試。"
            elif "inference capacity" in error_msg or "Service Unavailable" in error_msg:
                return "❌ 推論服務暫時不可用或過載，請稍後再試。"
            return f"❌ API 錯誤：{error_msg}"
        else:
            return "❌ API 回傳格式非預期。"

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
        return f"❌ HTTP 錯誤：{http_err} - {response.text}"
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return "❌ 請求超時：Hugging Face API 未在時間內回應。"
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection Error: {conn_err}")
        return f"❌ 連接錯誤：無法連接到 Hugging Face API。請檢查網路或 API 地址。"
    except requests.exceptions.RequestException as req_err:
        print(f"Request Exception: {req_err}")
        return f"❌ 請求錯誤：{req_err}"
    except Exception as e:
        print(f"Unexpected Error: {e}")
        return f"❌ 未知錯誤：{str(e)}"

# 首頁路由
@app.route("/")
def index():
    return render_template("index.html")

# 穿搭建議頁面
@app.route("/fashion", methods=["GET", "POST"])
def fashion():
    if request.method == "POST":
        # 圖片處理邏輯待補
        # 如果要處理圖片上傳，需要用 request.files.get()
        # 並可能需要一個外部服務或本地庫來處理圖像 AI 任務
        return render_template("fashion.html", result="建議：搭配亮色外套與俐落髮型。")
    return render_template("fashion.html")

# AI 對話訓練頁面
@app.route("/talking", methods=["GET", "POST"])
def talking():
    ai_response = None
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip() # 移除首尾空白
        if user_input:
            # 設計一個清晰的 prompt，以便於模型理解和提取回應
            # 讓模型明確知道它是一個「回答」
            prompt = f"You are a witty, flirty woman chatting with a man. He says: \"{user_input}\" What would you say in response?"
            
            ai_response = query_huggingface(prompt)
        else:
            ai_response = "請輸入你的對話內容。"
    return render_template("talking.html", ai_response=ai_response)

# 投資理財頁面
@app.route("/finance")
def finance():
    return render_template("finance.html")

if __name__ == "__main__":
    # 在生產環境中，應避免使用 debug=True，因為這會導致安全風險和性能問題
    # 在開發階段，debug=True 很有用，因為它會在程式碼變動時自動重載
    app.run(debug=True, host='0.0.0.0', port=5000) # 監聽所有網路接口，以便外部訪問