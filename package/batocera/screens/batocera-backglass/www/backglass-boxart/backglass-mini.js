function onSystem(infos) {
    var html = "";
    if(infos["logo"]) {
	html += "<div id=\"system_logo\"><div id=\"system_logo_internal\"><img src=\"" + infos["logo"] + "\" /></div></div>";
    } else {
	if(infos["fullname"]) {
	    html += "<div id=\"system_text\"><div id=\"system_text_internal\">" + infos["fullname"] + "</div></div>";
	}
    }
    document.getElementById("infos").innerHTML = html;
}

function onGame(infos) {
    var html = "";

    if(infos["thumbnail"]) {
	html += "<div id=\"game_boxart\"><div id=\"game_boxart_internal\"><img src=\"" + infos["thumbnail"] + "\" /></div></div>";
    } else {
	if(infos["name"]) {
	    html += "<div id=\"game_text\"><div id=\"game_text_internal\">" + infos["name"] + "</div></div>";
	}
    }
    document.getElementById("infos").innerHTML = html;
}
