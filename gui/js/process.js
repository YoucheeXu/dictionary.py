INDEX = 1
bMeaning = false;

function process_primary(tabAlign, dict_primary){
    var primary = dict_primary;
    var xml = "";
    if(primary instanceof Array){
        for(var i in primary){
            var data = primary[i];
			html = process_primary(tabAlign, data);
			// console.log("html1: " + html + ";");
			if(html.slice(0, 1) == "<"){
				xml += "\r\n" + tabAlign;
			}
			xml += html;
        }
    }
    else if(typeof(primary) == "object"){
        var hasChild = false;
        var hasType = false;
        if(primary.type != undefined){
            hasType = true;
            if(primary.type == "container"){
            	xml += "\r\n" + tabAlign + "<div class = 'wordtype'>" + primary.labels[0].text + ": </div>\r\n";
            	xml += tabAlign + "<div class = '" + primary.type + "1'>\r\n";
				tabAlign += "\t";
				html = process_terms(tabAlign, primary.terms, primary.type);
				if(html.slice(0, 1) == "<"){
					xml += "\r\n" + tabAlign;
				}
				xml += html;
            }else{
				if(primary.labels != undefined){
					// if(xml.substr(-1, 1) == ">"){
						// xml += "\r\n";
					// }
					xml += tabAlign + "<div class = '" + primary.type + "'>";
					tabAlign += "\t";
					xml += "\r\n" + tabAlign + "<div class = 'labels'>" + primary.labels[0].text + "</div>";
					html = process_terms(tabAlign, primary.terms, primary.type);
					if(html.slice(0, 1) == "<"){
						xml += "\r\n" + tabAlign;
					}
					xml += html;
				}
				else{
					if(primary.type == "meaning"){
						// console.log("xml: " + xml + ";");
						// xml += "X: "
						bMeaning = true;
					}
					console.log(bMeaning);
					if(primary.type == "example" && bMeaning == true){
						// console.log("xml: " + xml + ";");
						// xml += "Y: ";
						xml += "\r\n";
						bMeaning = false;
						console.log(bMeaning);
					}
					xml += tabAlign + "<div class = '" + primary.type + "'>";
					tabAlign += "\t";
					html = process_terms(tabAlign, primary.terms, primary.type);
					if(html.slice(0, 1) == "<"){
						xml += "\r\n" + tabAlign;
					}
					// console.log("html4: " + html + ";");
					xml += html;
				}
			}
            if(primary.entries != undefined){
				html = process_primary(tabAlign, primary.entries);
				// console.log("html: " + html + ";");
				// console.log("xml: " + xml + ";");
				// console.log("html2: " + html + ";");
				if(html.slice(0, 1) == "<"){
					xml += "\r\n" + tabAlign + "Q: ";
				}
				xml += html;
            }
            // xml += tabAlign + "</div>\r\n";
			tabAlign = tabAlign.slice(0, -1);
			// console.log(xml.substr(-3, 3));
			if(xml.substr(-3, 1) == ">"){
				xml += tabAlign;
			}
			if(xml.substr(-1, 1) == ">"){
				xml += "\r\n" + tabAlign;
			}
            xml += "</div>\r\n";
			// tabAlign = tabAlign.slice(0, -2);
        }
    }
    else if(typeof(primary) == "string"){
		html = process_primary(tabAlign, eval("(" + primary + ")"));
		// console.log("html3: " + html + ";");
		xml += html;
	}
    return xml;
}

function process_terms(tabAlign, dict_terms, type){
	var terms = dict_terms
	var xml = ""
	if(terms instanceof Array){
        for(var i in terms){
            var data = terms[i];
			html = process_terms(tabAlign, data, type);
			// if(html.slice(0,1) == "<"){
				// xml += "\r\n" + tabAlign;
			// }
			xml += html;
        }
    }
    else if(typeof(terms) == "object"){
        var hasType = false;
        if(terms.type != undefined){
            hasType = true;
            if(terms.type != "text" || type == "headword" || type =="related"){
				if(terms.type == "sound") {
					/*xml += '<div class="'+ terms.type + '">';
					//xml += terms.text +"</div>";
					xml += '<embed type="application/x-shockwave-flash" src="SpeakerApp16.swf"' +
						'width="20" height="20" id="movie28564" name="movie28564" bgcolor="#000000"' +
						'quality="high" flashvars="sound_name='+ terms.text + '"wmode="transparent">'
					xml += "</div>"*/
					// alert(terms.text);
					xml += getSound(tabAlign, terms.text);
				}
				else {
					// console.log("P: " + xml)
					// if(xml.substr(-1, 1) == ">"){
						// xml += "\r\n" + tabAlign;
					// }
					xml += "\r\n" + tabAlign + "<div class = '" + terms.type + "'>" + 
						terms.text + "</div>";
				}
            }
            else{
            	xml += terms.text;
            }
        }
    }
    return xml
}

function process_term(dict_terms){
	var terms = dict_terms

    for(var i in terms){
    	var data = terms[i];
        xml += (data.text);
    }
    return xml
}

function getChange(){
	var url = window.location.href;
	var index = url.search("word=");
	if(index != -1){
		word = url.substring(index + 5)
		var script = document.createElement('script');
		script.setAttribute('src', getUrl(word));
		document.getElementsByTagName('head')[0].appendChild(script); 
	}
}

function getUrl(word){
	var url = "http://www.google.com/dictionary/json?callback=getJson&q=" + word + "&sl=en&tl=zh-cn&restrict=pr,de&client=te"
	return url
}

function changeSound(){
	sounds = document.getElementsByClassName("sound");
	//sounds = document.getElementsByName("sound");
	for (i in sounds){
		html = getSound(escape(sounds[i].innerHTML));
		sounds[i].innerHTML = html;
		// alert(html);
		// loadPlayer();
	}
}

function getSound(tabAlign, url){
	sound = "\r\n" + tabAlign + "<div class = 'sound' id = 'Player'>\r\n" +
		tabAlign + "\t" + "<button class = 'jp-play' id = 'playpause' title = 'Play'></button>\r\n" +
		tabAlign + "\t" + "<audio id = 'myaudio'>\r\n" +
		tabAlign + "\t" + "\t" + "<source src = " + url + " type= 'audio/mpeg'>\r\n" +
		tabAlign + "\t" + "\t" + "Your browser does not support the audio tag.\r\n" +
		tabAlign + "\t" + "</audio>\r\n" +
		tabAlign + "</div>";
	return sound;
}

/*
// To-Do：dynamic set player
function getSound(url){
	sound = "<div id=\"jquery_jplayer_1\"></div>\r\n" +
		"<div id=\"jp_container_1\">\r\n" +
		"\t<div class=\"jp-controls\">\r\n" +
		"\t\t<button class=\"jp-play\" role=\"button\" tabindex=\"0\">play</button>\r\n" +
		"\t</div>\r\n" +
		"</div>\r\n"
	return sound;
}

function loadPlayer2(audio){
	var word = get_word();
	$("#jquery_jplayer_1").jPlayer({
		ready: function () {
		$(this).jPlayer("setMedia", {
			mp3: audio
		}).jPlayer("play");
		},
		supplied: "mp3",
		useStateClassSkin: true,
		keyEnabled: true
	});
}

// To-Do：dynamic load player
function loadPlayer(){
	var word = get_word();
	$("#jquery_jplayer_1").jPlayer({
		ready: function () {
		$(this).jPlayer("setMedia", {
			mp3: "../audio/Google/" + word + ".mp3"
		}).jPlayer("play");
		},
		supplied: "mp3",
		useStateClassSkin: true,
		keyEnabled: true
	});
}*/

/*function getSound(url){
	// sound = '<object data="http://www.google.com/dictionary/flash/SpeakerApp16.swf" \
		type = "application/x-shockwave-flash" width=" 16" height="16" id="pronunciation"> \
	// sound = '<object data="SpeakerApp16.swf" type="application/x-shockwave-flash" width=" 16" \
		// height="16" id="pronunciation">\
		// <param name="movie" value="Speaker.swf">\
		// <param name="flashvars" value="sound_name='+ url+'">\
	// </object>';
	// sound = '<embed type="application/x-shockwave-flash" src="SpeakerApp16.swf" width="20" \
		height="20" id="movie28564" name="movie28564" bgcolor="#000000" quality="high" \
		flashvars="sound_name=../../Audio/Google/class.mp3" wmode="transparent">';
	sound = '<embed type="application/x-shockwave-flash" src="SpeakerApp16.swf" \
		width="20" height="20" id="movie28564" name="movie28564" bgcolor="#000000" \
		quality="high" flashvars="sound_name='+ url + '"wmode="transparent">';
	return sound;
}*/

/*function getSound(url){
	//sound = '<a href = "javascript:;" class = "laba" onmouseover = "asplay(\'' + url +
		'\');" onmouseout = "clearTimeout(timer);" onclick = "asplay(\'' + url + '\');" ></a>'
	sound = '<div class="sound"><a href="javascript:;" class="laba" onmouseover="asplay(\'' + url +
		'\');" onmouseout ="clearTimeout(timer);" onclick="asplay(\'' + url + '\');" ></a></div>'
	return sound;
}*/

/*function getSound(url){
	sound = '<div class = "sound">\r\n<a href = "' + url +
		'" class = "laba" onmouseover = "asplay(\'' + url +'\');" onmouseout = "clearTimeout(timer);"></a>\r\n</div>\r\n'
	//sound = '<div class="sound"><a href="javascript:;" class="laba" onmouseover="asplay(\'' + url +
		'\');" onmouseout ="clearTimeout(timer);" onclick = \
		"response.setHeader("Content-disposition", "attachment;filename = \'"' + url + '\');" ></a></div>'
	return sound;
}*/

function getFlashObject_top(movieName) {
    if (window.document[movieName]) {
        return window.document[movieName];
    }   
    if (navigator.appName.indexOf("Microsoft Internet")==-1) {
        if (document.embeds && document.embeds[movieName])
          return document.embeds[movieName];
    } else  {
        return document.getElementById(movieName);
    }   
}

var timer = null;
function player_callback(c) {
    // var asound = getFlashObject_top("asound_top");
    // if(asound){
        // asound.SetVariable("f",c);
        // asound.GotoFrame(1);
		// //alert(c);
    // }
	// else alert("can't get asound_top!");
    return false;

}
function asplay(c){
    clearTimeout(timer);
    var mp3_1 = "player_callback('" + c + "')";
    timer = setTimeout(mp3_1, 100);
	//alert("haha!");
}

function formSubmit(){
	var value = document.getElementById("form_value");
	var word = value.value
	var script = document.createElement('script');
	script.setAttribute('src', getUrl(word));
	document.getElementsByTagName('head')[0].appendChild(script); 
	//alert(getUrl(word))
	script.onload = function() {
		var content = process_primary(dict.primaries);
		var webdef = process_primary(dict.webDefinitions);
		document.getElementById("content").innerHTML = content;
		changeSound();
		document.getElementById("webdef").innerHTML = webdef;
	}
	translate(word);
}

var search = function(searchbox){
	if(searchbox == undefined){searchbox="searchbox";}
	if(lastword == word){return;}
	var word=$(searchbox).value.trim().toLowerCase();
	if(word.match(/\w+/) == null){
		$(searchbox).value = "";
		$(searchbox).focus();
		//alert("请输入要查询的英文单词");return false;
	}
	if(word.length==0){$(searchbox).focus();return false;}
	
	window.location.href = g_word_prefix+"/"+word;
	return false;
}

function enter(){
	if (event.keyCode == 13){
		formSubmit();
	}
}

function translate(word){
	var url = "https://www.googleapis.com/language/translate/v2?key= \
		AIzaSyCTAervvQn5LZBCMgMcwHi4y5K7js71hU0&source=en&target=zh&callback=translateText&q=" + 
		word;
	var script = document.createElement('script');
	script.setAttribute('src',url);
	document.getElementsByTagName('head')[0].appendChild(script); 
	script.onload = function() {
		document.getElementById("translate").innerHTML = tl;
	}	
}

tl = null;
function translateText(response) {
	tl =  response.data.translations[0].translatedText;
}