function setGoodHeight (element) {
	if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
		var w = element.naturalWidth;
		var h = element.naturalHeight;
		element.setAttribute("style","width:90vw");
		var wn = element.width;
		var hn = h * wn / w;
		element.setAttribute("style","height:"+hn+"px");
	}
	else {
	    height_buffer = 100
	    width_buffer = 100
	    height_diff_pct = element.naturalHeight / window.innerHeight
	    width_diff_pct = element.naturalWidth / window.innerWidth
		if(height_diff_pct > width_diff_pct) {
			var h = element.naturalHeight;
			var w = element.naturalWidth;
			element.height = window.innerHeight - height_buffer;
			element.width = w * element.height / h;
		}
		else {
			var h = element.naturalHeight;
			var w = element.naturalWidth;
			element.width = window.innerWidth - width_buffer;
			element.height = h * element.width / w;
		}
		if(element.width < 540) {
			element.parentNode.setAttribute("style","width:" + 540 + "px");
		}
		else {
			element.parentNode.setAttribute("style","width:" + (element.width + 40) + "px");
		}
	}
}

function setGoodHeightForAll () {
    var works = document.getElementsByClassName("work");
    for(var i = 0; i < works.length; i++) {
        setGoodHeight(works[i])
    }
}

function newNoteHeight (element) {
	var h = element.height;
	element.parentNode.setAttribute("style","width:" + (h+40) + "px");
}

function snapScrollToImage () {
    work_title_element = document.getElementById("work_title");
    work_title_element.scrollIntoView(true);
}

function setSmallHeight (element, height) {
	element.width = 230;
	element.height = 230;
}