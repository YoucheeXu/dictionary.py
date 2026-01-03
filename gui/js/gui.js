gbCEFPython = false;

$(document).ready(function () {
	// console.log("#btn_prev:" + $("#btn_prev:disabled").css('background-position-x'));
	// console.log("#btn_next:" + $("#btn_next:disabled").css('background-position-x'));

    // top_panel
    initButton3("btn_menu", "./skin/menu_btn.bmp", 31, 21);
    initButton3("btn_min", "./skin/minimize_btn.bmp", 33, 21);
    initButton3("btn_max", "./skin/maxmize_btn.bmp", 33, 21);
    initButton3("btn_restore", "./skin/restore_btn.bmp", 33, 21);
    initButton3("btn_close", "./skin/close_btn.bmp", 43, 21);

    // input_panel
	initButton4("btn_prev", "./skin/prev_btn.bmp", 45, 37);
    initButton4("btn_next", "./skin/next_btn.bmp", 40, 37);
    initButton3("btn_del", "./skin/delete_item.bmp", 30, 34);
    initButton3("btn_drop", "./skin/combobox_drop_btn.bmp", 20, 34);
    initButton3("btn_lookup", "./skin/lookup_btn.bmp", 110, 37);

	// double click to query word
	document.addEventListener('dblclick', function(e){
		// console.log("Dobule Click!");
		// console.log(e);
		// console.log(e.target.id);
		if ("word_input" == e.target.id) return;

		var word = (document.selection && 
			document.selection.createRange().text) ||
			(window.getSelection && window.getSelection().toString());
		// log("info", "dblclick: " + word, false);
		word = word.trim();
		set_word(word);
		query_word(word);
	});

	// addTab("tab1", "tab1-haah", "");
	// addTab("tab2", "tab2-haah", "");

	// console.log("#btn_prev:" + $("#btn_prev:disabled").css('background-position-x'));
	// console.log("#btn_next:" + $("#btn_next:disabled").css('background-position-x'));

	if (navigator.appVersion.indexOf("Chrome/66.0.3359.181") > -1){
		gbCEFPython = true;
	}

	if(gbCEFPython){
		$("#tabContainer").tabs({
			data: [],
		})
	}
});

function initButton3(id, img, width, height){
    $("#" + id).css("background", "url(" + img + ")");
    $("#" + id).css('width', width);
    $("#" + id).css('height', height);
    $("#" + id).css('outline', 'none');
    $("#" + id).css('background-position', '0px 0px');
    $("#" + id).hover(function(){
        $(this).css('background-position-x', -1 * width);
    }, function(){
            $(this).css('background-position-x', 0);
        }
    );
    $("#" + id).mousedown(function(){
            $(this).css('background-position-x', -2 * width);
        }
	);
    $("#" + id).mouseup(function(){
            $(this).css('background-position-x', -1 * width);
        }
	);
}

function initButton4(id, img, width, height){
    $("#" + id).css("background", "url(" + img + ")");
    $("#" + id).css('width', width);
    $("#" + id).css('height', height);
    $("#" + id).css('outline', 'none');
    $("#" + id).css('background-position', '0px 0px');

    $("#" + id).hover(function(){
        $(this).css('background-position-x', -1 * width);
    }, function(){
            $(this).css('background-position-x', 0);
        }
    );
    $("#" + id).mousedown(function(){
            $(this).css('background-position-x', -2 * width);
        }
	);
    $("#" + id).mouseup(function(){
            $(this).css('background-position-x', -1 * width);
        }
	);

	// TODO: statements follow do not work as expection
	// console.log("#" + id + ":" + $("#" + id + ":disabled").css('background-position-x'));
	$("#" + id + ":disabled").css('background-position-x', -3 * width);
	$("#" + id + ":enabled").css('background-position-x', 0);
	// console.log("#" + id + ":" + $("#" + id + ":disabled").css('background-position-x'));
}

function disableButton(id, is) {
    if(is == true){
        var btn_width = $("#" + id).css('width').slice(0, -2);
		newXPos = -3 * parseInt(btn_width);
		$("#" + id).css('background-position-x', newXPos);
		$("#" + id).attr('disabled', 'disabled');
    }
    else{
		$("#" + id).removeAttr("disabled");
		$("#" + id).css('background-position-x', 0);
	}
}

function hideButton(id, is) {
    if(is == true){
        $("#" + id).hide();
    }
    else $("#" + id).show();
}

function set_word(word){
	$('#word_input').val(word)
}

function hide_words_list(){
	$('#words_list').hide();
	$("#contents_box").css("width", 701);
}

function get_word(){
	try {
		word = $('#word_input').val();
		// word = word.replace(/\ /g, "_");
		// 去除字符串内两头的空格
		word = word.replace(/^\s*|\s*$/g,"");
		// word = word.trim();
		// log("info", "get_word: " + word, false)
		set_word(word);
	}
    catch(error){
		log("error", error, true);
		return "";
    }	
    return word;
}

function query_word(word){

	if (word == null || word == undefined || word == ''){
		word = get_word();
	}

	if(word.length < 1){
		tabRef = get_active_tab_href();
        $(tabRef + ' p').html('');
		return false;
	}

	// log("info", "query_word: " + word, false)

	try {
		if(window.external) window.external.query_word(word);
		$('#word_input').focus();
		$('#word_input').select();
		return true;
    }
    catch(error){
		log("error", error, true);
    }

	return false;
}

function clear_input(){
    $('#word_input').val("");
	clear_words_list();
    $('#words_list').hide();
    $("#contents_box").css("width", 701);
    $('#panel1 p').html("");
}

$(":button").click(function(){
    // disableLink(link);
    var id = $(this).attr("id");
	// alert(id + " button is clicked!")
    if(id == "btn_lookup"){
		hide_words_list();
        query_word();	
	}
    else if(id == "btn_del") {
        clear_input();
    }
	else if(id == "btn_menu"){

	}
    // else if (window.external){
    else if (gbCEFPython){
		window.external.OnButtonClicked(id);
	}
});

$(".main_panel").mousedown(function(event){
	// alert(".top_panel" + event.clientX);
	// if(window.external){
	if(gbCEFPython){
		window.external.start_move(event.screenX, event.screenY);
	}
});

$(".main_panel").mousemove(function(event){
	// alert(".top_panel" + event.clientX);
	// if(window.external){
	if(gbCEFPython){
		window.external.moving(event.screenX, event.screenY);
	}
});

$(".main_panel").mouseup(function(event){
	// alert(".top_panel" + event.clientX);
	// if(window.external){
	if(gbCEFPython){
		window.external.stop_move(event.screenX, event.screenY);
	}
});

$(".main_panel").mouseleave(function(event){
	// alert(".top_panel" + event.clientX);
	// if(window.external){
	if(gbCEFPython){
		window.external.stop_move(event.screenX, event.screenY);
	}
});

$(function(){
$('#word_input').bind('keyup', function(event){
    if(event.keyCode == "13") {   //return key
        // alert('你输入的内容为：' + $('#word_input').val());
		hide_words_list();
		query_word();
    }
    else {
        var word = $('#word_input').val();
		// get current tabRef

        // $('#panel1 p').html('你输入的内容为：' + word);
		// tabRef = $(".nav-tabs").children('.active').attr('href');
		tabRef = get_active_tab_href();
		// log("info", tabRef, false);

        if(word.length >= 1) {
			$(tabRef + ' p').html('你输入的内容为：' + word);
			clear_words_list();
            $('#words_list').show();
            $("#contents_box").css("width", 500);
            try {
            	if (window.external) window.external.OnTextChanged(word);
            }
            catch(error){
				log("error", error, true);
            }
            // append_words_list(word);
        }
        else {
            // clear_input();
            $('#words_list').hide();
            $("#contents_box").css("width", 701);
			$(tabRef + ' p').html('');
        }
    }
    });
});

function playMP3(mp3){
	// $("#jquery_jplayer_1").jPlayer("play");
}

function clear_words_list(){
	var obj = document.getElementById('words_list');
	// 删除所有选项option
	obj.options.length = 0;
}

function append_words_list(word) {
    $("#words_list").append("<option value = 'n+1'>" + word + "</option>");
    // $("#words_list").append("<option value = '" + no + "'>" + word + "</option>");
	// alert("<option value = '" + no + "'>" + word + "</option>");
}

function TopMostOrNot(){
	// if(window.external){
	if(gbCEFPython){
		window.external.TopMostOrNot();
	}
}

function log(lvl, info, isException){
	try{
		console.log(info);

		// if(window.external){
		if(gbCEFPython){
			if(isException == true){
				info = "Name: " + info.nameinfo + "\n\t" +
					"message: " + info.message + "\n\t" +
					"description: " + info.description + "\n\t" +
					"stack: " + info.stack;
			}
			window.external.log(lvl, info);
		}
	}
	catch(error){
		console.log(error);
    }
}

function bindSwitchTab(){
	$(".nav-tabs li a").click(function () {
		try{
			// var id = $(this).attr("id");
			// log("info", "id: " + id, false);
			// eval(id + "_search()");
			// log("info", "SwitchTab", false);

			var tabId = $(this).attr("href");
			log("info", "Switch to : " + tabId, false);
			$(tabId + ' p').html('');

			tabId = tabId.slice(1);
			log("info", "tabId: " + tabId, false);
			// var n = parseInt(tabNum);
			if(window.external){
				window.external.switch_tab(tabId);
			}
			query_word();
		}
		catch(error){
			log("error", error, true);
		}

		$('#words_list').hide();
		$("#contents_list_box").css("width", 701);    
	})
}

function get_active_tab_href(){
	return $(".nav-tabs").find('li.active').children('a').attr('href');
}

function addTab(tabId, name, html){
	$("#tabContainer").data("tabs").addTab({tabId: tabId, name: name, closeable: true, html: html});
	console.log("addTab: ", tabId, name, html);
}

function activeTab(tabId){
	$("#tabContainer").data("tabs").showTab(tabId);
}

function bindMenus(){
	$(".dropdown-menu a").click(function () {
		var menuId = $(this).attr("href");

		menuId = menuId.slice(1);
		log("info", "menuId: " + menuId, false);

		// if(window.external){
		if(gbCEFPython){
			window.external.OnMenuClicked(menuId);
		}		
	})
}

function fill_menu(menuId, name){
	// <a class="dropdown-item" href="#XX-Net">XX-Net</a>
	item = '<a class="dropdown-item" href="#{0}">{1}</a>'.format(menuId, name)
	$("#sys_menu").append(item)
}

function active_menu(menuId){
	// var $a = $("#sys_menu a")
	// console.log($a);
	// href = $a.attr("href");

	// var ch = $("#ff").find("input");
	// console.log(ch.length);
	// for (var i=0; i <ch.length; i++) {
		// console.log(ch.eq(i));
	// }

	var as = $("#sys_menu a")
	// console.log(as.length);
	for (var i = 0; i <as.length; i++) {
		var a = as.eq(i);
		// console.log(a);
		href = a.attr("href");
		// console.log(href)
		if(href != "#" + menuId){
			a.removeClass("active");
		}
		else{
			a.addClass("active");
		}
	}
}