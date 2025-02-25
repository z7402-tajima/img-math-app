import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
import numpy as np

classes = ["0","1","2","3","4","5","6","7","8","9"]
image_size = 28

UPLOAD_FOLDER = "uploads" # アップロードされた画像を保存するフォルダ名
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif']) # アップロードを許可する拡張子

app = Flask(__name__)

# app.secret_key = "your_secret_key_here"  
# submitボタンを押した際にエラーが出た場合上の行のコメントアウトを削除し、your_secret_key_hereに任意の文字列（例:aidemy)を指定し、再度アプリケーションを実行してください。

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

model = load_model('./model.keras') # 学習済みモデルをロード

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    pred_answer = "画像を送信してください"

    if request.method == 'POST':
        if 'file' not in request.files: # ファイルデータが含まれていない
            flash('ファイルがありません')
            return redirect(request.url) # リクエスト元のURLにリダイレクト
        file = request.files['file']
        if file.filename == '': # ファイルにファイル名がない
            flash('ファイルがありません')
            return redirect(request.url) # リクエスト元のURLにリダイレクト
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename) # サニタイズ: ファイル名にある危険な文字列を無効化
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            filepath = os.path.join(UPLOAD_FOLDER, filename)

            # 受け取った画像を読み込み、numpyの配列形式に変換
            img = image.load_img(filepath, color_mode='grayscale', target_size=(image_size,image_size))
            img = image.img_to_array(img)
            data = np.array([img])
            # 変換したデータをモデルに渡して予測する
            result = model.predict(data)[0]
            predicted = result.argmax()
            pred_answer = "この画像の数字は[" + classes[predicted] + "]です"

    # 対応づけられたURLのページにhtmlを反映させる(htmlファイルはtemplatesフォルダに置く)
    return render_template("index.html",answer=pred_answer)

if __name__ == "__main__":
    # ローカル実行時
    #app.run()
    # 外部公開設定時
    port = int(os.environ.get('PORT', 8080)) # Renderで使えるポート番号を取得（未設定時は8080）
    app.run(host ='0.0.0.0',port = port) # サーバーを外部からも利用可能にする
