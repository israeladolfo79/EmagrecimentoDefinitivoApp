document.getElementById("btn_convert1").addEventListener("click", function() {
	html2canvas(document.getElementById("download")).then(function (canvas) {			var anchorTag = document.createElement("a");
			document.body.appendChild(anchorTag);
			document.getElementById("previewImg").appendChild(canvas);
			anchorTag.download = "filename.jpg";
			anchorTag.href = canvas.toDataURL();
			anchorTag.target = '_blank';
			anchorTag.click();
		});
 });