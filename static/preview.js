function preview(obj, id) {
    // 前回のプレビュー表示を消す
    document.querySelector(id).innerHTML = '未選択';

    let fileReader = new FileReader();

    fileReader.onload = (function(e) {
        //document.getElementById(id).src = fileReader.result;
        document.querySelector(id).innerHTML = '<img class="preview" src="' + e.target.result + '">';
    });
    // プレビュー表示
    fileReader.readAsDataURL(obj.files[0]);
}
