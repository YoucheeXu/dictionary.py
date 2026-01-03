$(document).ready(function () {
    // top_panel
    initButton3("btn_menu", "./skin/menu_btn.bmp", 31, 21);
    initButton3("btn_min", "./skin/minimize_btn.bmp", 33, 21);
    initButton3("btn_max", "./skin/maxmize_btn.bmp", 33, 21);
    initButton3("btn_restore", "./skin/restore_btn.bmp", 33, 21);
    initButton3("btn_close", "./skin/close_btn.bmp", 43, 21);

    // input_panel
    initButton3("btn_next", "./skin/next_btn.bmp", 40, 37);
    initButton3("btn_del", "./skin/delete_item.bmp", 30, 34);
    initButton3("btn_drop", "./skin/combobox_drop_btn.bmp", 20, 34);
    initButton3("btn_lookup", "./skin/lookup_btn.bmp", 110, 37);
});

function disableButton(id, is) {
    if(is == true){
        $("#"+id).attr('disabled', 'disabled');
    }
    else $("#"+id).removeAttribute("disabled");
};

function hideButton(id, is) {
    if(is == true){
        $("#"+id).hide();
    }
    else $("#"+id).show();
};

function initButton3(id, img, width, height){
    $("#"+id).css("background", "url(" + img + ")");
    $("#"+id).css('width', width);
    $("#"+id).css('height', height);
    $("#"+id).css('outline', 'none');
    $("#"+id).css('background-position', '0px 0px');
    $("#"+id).hover(function(){
        $(this).css('background-position-x', -1 * width);
    }, function(){
            $(this).css('background-position-x', 0);
        }
    );
    $("#"+id).mousedown(function(){
            $(this).css('background-position-x', -2 * width);
        });
    $("#"+id).mouseup(function(){
            $(this).css('background-position-x', -1 * width);
        });
    // <!-- $("#"+id).disabled(function(){ -->
        // <!-- $(this).css('background-position-x', -3 * width); -->
    // <!-- }, function(){ -->
        // <!-- $(this).css('background-position-x', 0); -->
    // <!-- }); -->
    // alert($("#btn_prev").css('hover'));
}

function get_word(){
    word = $('#word_input').val();
    word = word.replace(/\ /g, "_");
    // alert("Got word: " + word);
    return word;
}

function query_word(){
	var word = get_word();
	// alert("query word: " + word);

	$('#words_list').hide();
	$("#contents_box").css("width", 701);

	try {
		if(window.external) window.external.QueryWord(word);
		$('#word_input').focus();
		$('#word_input').select();
    }
    catch(error){
        google_search();
        console.log(error);
        // alert(error);
    }
    // $("#google").tab('show');
}

function clear_input(){
    $('#word_input').val("");
    $('#words_list').hide();
    $("#contents_box").css("width", 701);
    $('#panel1 p').html("");
}

$(":button").click(function(){
    // disableLink(link);
    var id = $(this).attr("id");
	// alert(id + " button is clicked!")
    if(id == "btn_lookup"){
		query_word();
	}
    else if(id == "btn_del") {
        clear_input();
    }
    // else if (window.external) window.external.OnButtonClicked(id);
});

$(".top_panel").mousedown(function(event){
	// alert(".top_panel" + event.clientX);
	if(window.external) window.external.startMove(event.screenX, event.screenY);
});

$(".top_panel").mousemove(function(event){
	// alert(".top_panel" + event.clientX);
	if(window.external) window.external.moving(event.screenX, event.screenY);
});

$(".top_panel").mouseup(function(event){
	// alert(".top_panel" + event.clientX);
	if(window.external) window.external.stopMove(event.screenX, event.screenY);
});

$(".top_panel").mouseleave(function(event){
	// alert(".top_panel" + event.clientX);
	if(window.external) window.external.stopMove(event.screenX, event.screenY);
});

$(function(){
$('#word_input').bind('keyup', function(event){
	// if (window.external) window.external.log(event);
	// console.log(error);
    if(event.keyCode == "13") {   //return key
        // alert('你输入的内容为：' + $('#word_input').val());
        query_word();
    }
    else {
        var word = $('#word_input').val();
        $('#panel1 p').html('你输入的内容为：' + word);
        if(word.length >= 2) {
            $('#words_list').show();
            $("#contents_box").css("width", 500);
            var obj = document.getElementById('words_list');
            // 删除所有选项option
            obj.options.length = 0;
            // 添加一个选项
            // obj.options.add(new Option(word)); //这个兼容IE与firefox
            try {
            	if (window.external) window.external.OnTextChanged(word);
            }
            catch(error){
				console.log(error);
            }
            // append_words_list(word);
        }
        else {
            // clear_input();
            $('#words_list').hide();
            $("#contents_box").css("width", 701);
        }
    }
    });
});

function playMP3(mp3){
	// $("#jquery_jplayer_1").jPlayer("play");
}

function append_words_list(word) {
    $("#words_list").append("<option value = 'n+1'>" + word + "</option>");
    // $("#words_list").append("<option value = '" + no + "'>" + word + "</option>");
	// alert("<option value = '" + no + "'>" + word + "</option>");
}

function addTab(){
	// <li>
		// <a href = "#panel4" id = "googleenglish" data-toggle = "tab" >Google English</a>
	// </li>

	// <div id = "panel4" class = "tab-pane">
		// <!-- <first style = "display: none">true</first> -->
		// <h4>to come soon</h4>
		// <p></p>
	// </div>
}