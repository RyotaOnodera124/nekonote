import os
from flask import Flask, render_template
from flask import Flask, request, abort, redirect, url_for
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from peewee import CharField, TextField, Model
from playhouse.db_url import connect

load_dotenv()

app = Flask(__name__)

line_bot_api = LineBotApi(os.environ["ACCESS_TOKEN"])
handler = WebhookHandler(os.environ["CHANNEL_SECRET"])

# データベースへの接続設定
db = connect(os.environ.get("DATABASE"))  # 環境変数に合わせて変更する場合

if not db.connect():
    print("接続NG")
    exit()


# モデルの定義
class Job(Model):
    location = CharField()
    description = TextField()
    work_day = CharField()
    working_hours = CharField()
    hourly_wage = CharField()
    contact = CharField()

    class Meta:
        database = db
        table_name = "jobs"


# テーブルが存在しない場合は作成
db.create_tables([Job], safe=True)


@app.route("/")
def index():
    return render_template("job_registration.html")


@app.route("/push_sample")
def push_sample():
    user_id = os.environ["USER_ID"]
    line_bot_api.push_message(user_id, TextSendMessage(text="Hello World!"))
    return "OK"


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError as e:
        abort(400)

    return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=event.message.text))


# /register_job エンドポイントを追加
@app.route("/register_job", methods=["POST"])
def register_job():
    if request.method == "POST":
        location = request.form.get("location")
        description = request.form.get("description")
        work_day = request.form.get("work_day")
        working_hours = request.form.get("working_hours")
        hourly_wage = request.form.get("hourly_wage")
        contact = request.form.get("contact")

    # データベースにデータを保存
        job = Job.create(
            location=location,
            description=description,
            work_day=work_day,
            working_hours=working_hours,
            hourly_wage=hourly_wage,
            contact=contact,
        )

        # 登録完了画面にリダイレクト
        return redirect(url_for("registration_complete", location=location,
                                description=description, work_day=work_day,
                                working_hours=working_hours, hourly_wage=hourly_wage, contact=contact))
    else:
        return "Method Not Allowed"


@app.route("/registration_complete")
def registration_complete():
    # リクエストのクエリパラメータからフォームデータを取得
    location = request.args.get("location")
    description = request.args.get("description")
    work_day = request.args.get("work_day")
    working_hours = request.args.get("working_hours")
    hourly_wage = request.args.get("hourly_wage")
    contact = request.args.get("contact")

    return render_template("registration_complete.html", location=location, description=description, work_day=work_day, working_hours=working_hours, hourly_wage=hourly_wage, contact=contact)


@app.route("/registration_success")
def registration_success():
    return render_template("registration_success.html")


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=8080)
