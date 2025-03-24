import os
from flask import Flask, request, redirect, render_template, flash
from werkzeug.utils import secure_filename
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.preprocessing import image
import numpy as np

app = Flask(__name__)
app.secret_key = "53CR3T" # シークレットキー

# 定数定義
num_classes = ["０","１","２","３","４","５","６","７","８","９"]
ope_classes = ["＋","－","×","÷"] # 0:＋, 1:－, 2:×, 3:÷
image_size = 28
img_list = ["img1", "img2", "img3"]
rdo_prefix = "rdo_"
upload_folder = "upload" # アップロード画像を一時的に保持するフォルダ名
allowed_extensions = set(["png", "jpg", "jpeg", "gif"]) # アップロードを許可する拡張子

# 学習済みモデルをロード
number_model = load_model("./model/number.keras") # 数字
operator_model = load_model("./model/operator.keras") # 演算子

@app.route("/", methods=["GET", "POST"])
def upload_file():
    answer = ""

    # 予測リスト：[種別, 値]の形式とし、リストinリストの形式で格納
    # 種別：1:数字、2:演算子
    # 値：0～9 (演算子の場合、0:＋, 1:－, 2:×, 3:÷)
    pred_list = []

    # 画像送信時
    if request.method == "POST":
        i = 0 # インデックス
        pred_answer = ""

        for img in img_list:
            i += 1
            # 未入力チェック：未入力の場合はその時点までの読み込んだ画像で計算を実施する
            if img not in request.files:
                flash(str(i) + "枚目にファイルが選択されていません")
                return redirect(request.url)
            file = request.files[img]
            if rdo_prefix + img not in request.form:
                flash(str(i) + "枚目に数字か演算子のチェックがありません")
                return redirect(request.url)
            kind = request.form[rdo_prefix + img]

            # 入力バリデーションチェック
            if file.filename == "":
                flash(str(i) + "枚目にファイルが選択されていません")
                return redirect(request.url)
            if kind != "1" and kind != "2":
                flash(str(i) + "枚目の選択項目の値が不正です")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename) # サニタイズ: ファイル名にある危険な文字列を無効化
                file.save(os.path.join(upload_folder, filename))
                filepath = os.path.join(upload_folder, filename)

                # 受け取った画像を読み込み、numpyの配列形式に変換
                img = image.load_img(filepath, color_mode="grayscale", target_size=(image_size, image_size))
                img = image.img_to_array(img)
                data = np.array([img])

                # 変換したデータをモデルに渡して予測する
                if kind == "1":
                    # 数字モデルで予測
                    result = number_model.predict(data)[0]
                    predicted = result.argmax()
                    pred_answer += num_classes[predicted]
                    # 予測リストに格納
                    pred_list.append([int(kind), int(predicted)])
                else:
                    # 演算子モデルで予測
                    result = operator_model.predict(data)[0]
                    predicted = result.argmax()
                    pred_answer += ope_classes[predicted]
                    # 予測リストに格納
                    pred_list.append([int(kind), int(predicted)])

                # 一時的にアップロードされた画像を削除
                os.remove(filepath)
            else:
                flash(str(i) + "枚目は画像ファイルではありません")
                return redirect(request.url)
            pred_answer += " "

        # 計算処理を実施
        cal = calculate(pred_list)
        answer = pred_answer + "= " + cal

    else: # GET method
        answer += "ここに計算結果が表示されます"

    return render_template("index.html",answer=answer)

# 許可された画像ファイルかをチェック
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions

# 計算処理
def calculate(pred_list):
    answer = ""    # 解答
    num = 0        # 現在の数値
    num_list = []  # 数字のリスト
    ope_list = []  # 演算子のリスト
    isDupFlg = True # 演算子重複フラグ

    try:
        # 予測リストをもとに、数字と演算子のリストに分ける
        for pred in pred_list:
            if pred[0] == 1:
                # 数字が連続している場合は、1つの数値とみなす
                num = num * 10 + pred[1]
                isDupFlg = False # 重複フラグをオフ
            else:
                if isDupFlg:
                    # 演算子が連続で設定されている場合（先頭にある場合も連続とみなす）
                    raise ValueError("演算子が先頭もしくは連続で設定されています")
                else:
                    num_list.append(num)
                    ope_list.append(pred[1])
                    num = 0
                isDupFlg = True # 重複フラグをオン

        # 末尾が演算子でない場合、最後の数値をリストに加える
        if not isDupFlg:
            num_list.append(num)

        # 数字と演算子のリスト要素数の整合性チェック
        if len(num_list) - len(ope_list) != 1:
            raise ValueError("式が成立していません")
        else:
            i = 0
            j = 0
            # Todo
    except ZeroDivisionError as e:
        answer = "ゼロ除算があります"
    except ValueError as e:
        answer = str(e)
    # 汎用例外処理は行わない（開発時のみチェック）
    #except Exception as e:
    #    answer = str(e)
    else:
        answer = "Todo"
    finally:
        return answer

# メイン
if __name__ == "__main__":
    # ローカル実行時
    #app.run()
    # 外部公開設定時
    port = int(os.environ.get("PORT", 8080))
    app.run(host ="0.0.0.0",port = port)
# EOF