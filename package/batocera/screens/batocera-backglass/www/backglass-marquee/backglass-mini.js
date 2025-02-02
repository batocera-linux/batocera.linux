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

    if(infos["marquee"]) {
	html += "<div id=\"game_marquee\"><div id=\"game_marquee_internal\">";
	if (infos["marquee"].endsWith(".mp4") || infos["marquee"].endsWith(".avi")) {
	    html += "<video autoplay loop\"><source src=\"" + infos["marquee"] + "\" /></video>"
	} else {
	    html += "<img src=\"" + infos["marquee"] + "\" />";
	}
	html += "</div></div>";
    } else {
	if(infos["name"]) {
	    html += "<div id=\"game_text\"><div id=\"game_text_internal\">" + infos["name"] + "</div></div>";
	}
    }
    document.getElementById("infos").innerHTML = html;
}
