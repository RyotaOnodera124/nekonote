# jobs_app.py

from flask import Flask, render_template
from peewee import CharField, TextField, Model, FloatField, SqliteDatabase

app = Flask(__name__)

# データベースの設定
db = SqliteDatabase("jobs.db")  # データベースファイルのパスを指定


# 求人情報のモデルを定義
class Job(Model):
    location = CharField()
    description = TextField()
    work_day = CharField()
    working_hours = CharField()
    hourly_wage = FloatField()
    contact = CharField()

    class Meta:
        database = db
        table_name = "jobs"


# データベースとテーブルの作成
db.connect()
db.create_tables([Job], safe=True)


# 求人情報の一覧を表示するエンドポイント
@app.route("/jobs")
def job_list():
    jobs = Job.select()  # データベースから求人情報を取得
    return render_template("jobs_list.html", jobs=jobs)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
