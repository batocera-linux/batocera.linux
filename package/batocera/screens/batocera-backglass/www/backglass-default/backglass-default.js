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
	html += "<div id=\"game_marquee\"><img src=\"" + infos["marquee"] + "\" /></div>";
    } else {
	if(infos["name"]) {
	    html += "<div id=\"game_name\">" + infos["name"] + "</div>";
	}
    }

    if(infos["image"]) {
	if(screen.width > screen.height) {
	    html += "<div id=\"game_image_horizontal\"><div id=\"game_image_internal_horizontal\"><img src=\"" + infos["image"] + "\" /></div></div>";
	} else {
	    html += "<div id=\"game_image_vertical\"><div id=\"game_image_internal_vertical\"><img src=\"" + infos["image"] + "\" /></div></div>";
	}
    }
    //if(infos["video"]) {
    //	html += "<div id=\"game_video\"><video autoplay=\"true\"><source src=\"" + infos["video"] + "\" /></video></div>";
    //}
    if(infos["desc"]) {
	if(screen.width > screen.height) {
	    html += "<div id=\"game_description_horizontal\"><div id=\"game_description_internal_horizontal\">" + infos["desc"] + "</div></div>";
	} else {
	    html += "<div id=\"game_description_vertical\"><div id=\"game_description_internal_vertical\">" + infos["desc"] + "</div></div>";
	}
    }

    document.getElementById("infos").innerHTML = html;
}
