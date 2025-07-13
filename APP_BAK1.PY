from flask import Flask, render_template, request
import firebase_admin
from firebase_admin import credentials

app = Flask(__name__)

# 初始化 Firebase
cred = credentials.Certificate("firebase_config.json")
firebase_admin.initialize_app(cred)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/fashion", methods=["GET", "POST"])
def fashion():
    if request.method == 'POST':
        image = request.files["photo"]
        # 可整合 Google Cloud Vision 或自訓模型
        return render_template("fashion.html", result="建議：搭配亮色外套與俐落髮型。")
    return render_template("fashion.html")

@app.route("/talking")
def talking():
    return render_template("talking.html")

@app.route("/finance")
def finance():
    return render_template("finance.html")

if __name__ == "__main__":
    app.run(debug=True)
