function preview_num1(obj) {
    // 前回のプレビュー表示を消す
    document.querySelector('#preview_num1').innerHTML = '';

    for (i = 0; i < obj.files.length; i++) {
        let fileReader = new FileReader();
        // onloadイベントハンドラ
        fileReader.onload = ((e)=> {
            // 読み込んだ画像をDataURLとして要素に設定
            document.querySelector('#preview_num1').innerHTML += '<img src="' + e.target.result + '">';
        });
        // DataURLとして読み込む
        fileReader.readAsDataURL(obj.files[i]);
    }
}
