import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
import numpy as np

num_classes = ["0","1","2","3","4","5","6","7","8","9"]
ope_classes = ["0","1","2","3"] # 0:+, 1:-, 2:*, 3:/
image_size = 28

NUMBERS_FOLDER = "number" # 数字の画像を保持するフォルダ名
OPERATORS_FOLDER = "operator" # 演算子の画像を保持するフォルダ名
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) # アップロードを許可する拡張子

app = Flask(__name__)
app.secret_key = "53CR3T" # シークレットキー

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 学習済みモデルをロード
number_model = load_model('./model/number.keras') # 数字
operator_model = load_model('./model/operator.keras') # 演算子

# name属性名定義
num_list = ['num1', 'num2']
ope_list = ['ope1']

# 画像リスト
num_files = []
ope_files = []

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # 変数初期化
    pred_answer = ''

    # 画像送信時
    if request.method == 'POST':
        if 'num1_img' not in request.files:
            flash('ファイルがありません')
            return redirect(request.url)
        file = request.files['num1_img']

        if file.filename == '':
            flash('ファイル名がありません')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # サニタイズ: ファイル名にある危険な文字列を無効化
            file.save(os.path.join(NUMBERS_FOLDER, filename))
            filepath = os.path.join(NUMBERS_FOLDER, filename)

            # 受け取った画像を読み込み、numpyの配列形式に変換
            img = image.load_img(filepath, color_mode='grayscale', target_size=(image_size,image_size))
            img = image.img_to_array(img)
            data = np.array([img])
            # 変換したデータをモデルに渡して予測する
            result = number_model.predict(data)[0]
            #result = operator_model.predict(data)[0]
            predicted = result.argmax()
            pred_answer += num_classes[predicted]

            # 最後にアップロードされた画像を削除
            os.remove(filepath)
        else:
            flash('画像ファイルではありません')
            return redirect(request.url)

    else: # GET method
        pred_answer += "ここに計算結果が表示されます"

    return render_template("index.html",answer=pred_answer)

if __name__ == "__main__":
    # ローカル実行時
    #app.run()
    # 外部公開設定時
    port = int(os.environ.get('PORT', 8080))
    app.run(host ='0.0.0.0',port = port)
# EOF