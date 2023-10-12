import os
import logging
from playhouse.db_url import connect
from dotenv import load_dotenv
from peewee import Model, CharField, TextField, FloatField

# .envの読み込み
load_dotenv()

# ①実行したSQLをログで出力する設定
logger = logging.getLogger("peewee")
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

# データベースへの接続設定
db = connect(os.environ.get("DATABASE"))  # 環境変数に合わせて変更する場合

# 接続NGの場合はメッセージを表示
if not db.connect():
    print("接続NG")
    exit()


# ③求人情報のモデル
class Job(Model):
    """Job Model"""

    location = CharField()
    description = TextField()
    working_hours = CharField()
    hourly_wage = FloatField()
    contact = CharField()

    class Meta:
        database = db
        table_name = "jobs"


# テーブルが存在しない場合は作成
db.create_tables([Job], safe=True)
