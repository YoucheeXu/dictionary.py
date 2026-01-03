$(document).ready(function () {
	// JQuery code to be added in here.
	//alert('doc ready')
	//norm_search();
	//ajax_search();
	//$('#search_box').focus();
	//google_search();
	//alert('\x26quot;');
});

$(".nav-tabs li a").click(function () {
    var id = $(this).attr("id");
    // switch(id) {
    // case "collocation" :
        // alert("case " + id + " was clicked!");
        // break;
    // case "googleenglish" :
        // googleenglish_search();
        // break;
    // }
    eval(id + "_search()");
    $('#words_list').hide();
    $("#contents_list_box").css("width", 701);    
})

function load_word(word, audio){
	html = "\n					<div class = 'text'>" + word + "</div>\n" + 
		"					<div class = 'sound' id = 'Player'>\n" + 
		"						<button class = 'jp-play' id = 'playpause' title = 'Play'></button>\n" + 
		"						<audio autoplay = 'autoplay' id = 'myaudio'>\n" + 
		"							<source src = " + audio + " type = 'audio/mpeg'>\n" + 
		"							Your browser does not support the audio tag.\n" + 
		"						</audio>\n" + 
		"					</div>\n" + 
		"					<ul class = 'stars'>\n" + 
		"						<li>★</li>\n" + 
		"						<li>★</li>\n" + 
		"						<li>★</li>\n" + 
		"						<li>★</li>\n" + 
		"						<li>★</li>\n" + 
		"					</ul>\n				";
	return html;
}

function google_dict(word, dict, audio){

	if ($('#panel1 first').html() == "false") {
		// alert("google_first: " + $('#panel1 first').html());
		return;
	}
	// alert(dict);
	// alert(audio);
	// var obj = eval("(" + dict + ")");
	// if (obj.ok != false) {
		// var obj = eval("(" + obj.info + ")");
		// var display = process_primary(obj.primaries);
		// $('#panel1 p').html(display);
		// // loadPlayer();
		// loadPlayer2(audio);
	// } else {
		// google_suggest(word);
		// // alert("no such " + word + " in google");
		// window.external.wrongJson(word);
	// }

	var obj = eval("(" + dict + ")");
	var tabAlign = "\t\t\t\t\t\t\t";
	var display = "\r\n" + process_primary(tabAlign + "\t", obj.primaries) + tabAlign;
	$('#panel1 p').html(display);
	$(".Word").html(load_word(word, audio));
	load_starts(0);
	loadPlayer();

	$('#panel1 first').html("false");
}

function google_search(){
	// alert(google_search)
	if ($('#panel1 first').html() == "false") {
		// alert("google_first: " + $('#panel1 first').html());
		return;
	}

	// var word = $('#queryword').html();
	// word = word.replace(/\ /g, "_");
	var word = get_word();
	// alert(word)

	var furl = 'http://www.google.com/dictionary/json?callback=dict_api.callbacks.id100&q=test&sl=en&tl=en&restrict=pr%2Cde&client=te';
	var furl2 = 'http://dictionary.so8848.com/ajax_search/?q=class';
	var curl2 = '../dict/Google/' + word.substr(0, 1) + '/' + word + '.json';

	var url = "";
	if(word == "class2"){
		url = furl2;
	}
	else{
		url = curl2;
	}
	// alert(document.documentMode);
	// alert("google_url: " + url);

	$.ajax({
		type:'GET',
		url: url,
		datatype: 'json',
		cache: false,
		//async: false,
		success: function(data){
			var obj = eval("(" + data + ")");
			if (obj.ok != false) {
				var obj = eval("(" + obj.info + ")");
				var display = process_primary(obj.primaries);
				$('#panel1 p').html(display);
				loadPlayer();
				//changeSound();
				/*if (display.length > 1000) {
					$('#button_ads').attr('style', '');
				}
				$.get('http://dictionary.so8848.com/suggestion', {
					q : word
				}, function (data) {
					$('.wordtype').first().before(data);
				});*/
				// window.external.OnSaveHtml(display);
				// alert("google_success: " + word);
			} else {
				/*$.get('http://dictionary.so8848.com/suggestion', {
					q : word
				}, function (data) {
					$('#toggle_example').first().after(data.replace("Similar", "Wow, not in the dict. Check out the suggested"));
					alert("fail: " + data);
				});
				alert("fail: " + word);*/
				google_suggest(word);
				// alert("no such " + word + " in google");
				window.external.wrongJson(word);
			}
		},
		/*error: function(err){
			$('#panel1 p').html("can't find " + word + " in google");
            // alert("can't find " + word + " in google");
		}*/
		error: function(XMLHttpRequest, textStatus, errorThrown){   
					// alert(XMLHttpRequest.status);  
					// alert();
					// alert('读取超时，请检查网络连接');
					$('#panel1 p').html("error occur when find " + word + " in google" + "<br>" + XMLHttpRequest.status + "<br>" + XMLHttpRequest.readyState + "<br>" + textStatus);
					// alert("error occur when find " + word + " in google");
		}
	});

	$('#panel1 first').html("false");
}

function google_suggest(word) {
	var curl2 = 'http://dictionary.so8848.com/suggestion/?q=' + word;
	// alert(curl2);
	$.ajax({
		type:'get',
		url: curl2,
		datatype: 'json',
		cache: false,
		//async: false,
		success: function(data){
			$('#toggle_example').first().after(data.replace("Similar", "Wow, not in the dict. Check out the suggested"));
			// alert("google_suggest fail: " + data);		
		},
		error: function(err){
			$('#panel1 p').html("can't find the suggestion of " + word + " in google");
		}
	});
}

function ajax_search() {
	// word = $('#queryword').html();
    // word = word.replace(/\ /g, "_");
    var word = get_word();
    // alert("ajax_search: " + word);
    
	$.get('http://dictionary.so8848.com/ajax_search', {
		q : word
	}, function (data) {
		var obj = eval("(" + data + ")");
		if (obj.ok != false) {
			var obj = eval("(" + obj.info + ")");
			var display = process_primary(obj.primaries)
				$('#panel1 p').html(display)
				changeSound();
			if (display.length > 1000) {
				$('#button_ads').attr('style', '');
			}
			$.get('http://dictionary.so8848.com/suggestion', {
				q : word
			}, function (data) {
				$('.wordtype').first().before(data);
			});
		} else {
			$.get('http://dictionary.so8848.com/suggestion', {
				q : word
			}, function (data) {
				$('#toggle_example').first().after(data.replace("Similar", "Wow, not in the dict. Check out the suggested"));
			});
		}
	});
}

function norm_search() {
	content = $('#searchresult').html();
	var obj = eval("(" + content + ")");
	var word = $('#queryword').html();
	if (obj.ok != false) {
		var obj = eval("(" + obj.info + ")");
		var display = process_primary(obj.primaries)
			$('#content').html(display);
		changeSound();
		if (display.length > 1500) {
			$('#button_ads').attr('style', '');
		}
		$.get('/suggestion', {
			q : word
		}, function (data) {
			$('.wordtype').first().before(data);
		});
	} else {
		$.get('/suggestion', {
			q : word
		}, function (data) {
			$('#toggle_example').first().after(data.replace("Similar", "Wow, not in the dict. Check out the suggested"));
		});
	}
}

// $('#collocation').click(function(){})
function collocation_search(){
	if ($('#panel2 first').html() != "true") {
		// alert("collocation_first: " + $('#panel2 first').html());
		return;
	}
	// word = $('#queryword').html();
    // word = word.replace(/\ /g, "_");
    var word = get_word();
	// alert("collocation: " + word);

	$.get('http://dictionary.so8848.com/ajax_collocation_search', {
		q : word
	}, function (data) {
		$('#panel2 p').html(data);
	});
	$('#panel2 first').html("false");
}

// $('#wordnet').click(function(){});
function wordnet_search(){
    if ($('#panel3 first').html() != "true") {
		// alert("wordnet_first: " + $('#panel3 first').html());
		return;
	}
    
	// var word = $('#queryword').html();
	// word = word.replace(/\ /g, "_");
    var word = get_word();
    // alert("wordnet: " + word);

	var curl = 'http://wordnet-online.freedicts.com/ajax/' + word;
	//curl = "http://gdicts.com/word/meaning/good";
	//alert("wordnet_curl: " + curl);

	/*$.getJSON(curl, function(data){
	  console.log(data.title); // Logs "jQuery Howto";
	alert('getJSON');});
	
	
	$.ajax({
	  type:     "GET",
	  url:      "https://graph.facebook.com/10150232496792613",
	  dataType: "jsonp",
	  success: function(data){
	      alert(data.id);
	      $('##panel3 p').html(data.id);
	  }});*/	

	var request = $.ajax({
			//url: "http://wordnet-online.freedicts.com/ajax/good",
			url : curl,
			type : "GET",
			dataType : "text",
			crossDomain : true
		});

	request.success(function (data) {
		$('#panel3 p').html(data);
	});

	request.done(function (msg) {
		//  $( "#log" ).html( msg );
		// alert('request sucess');

	});

	request.fail(function (xhr, textStatus, ajaxOptions, thrownError) {
		$('#panel3 p').html("cannot find " + word + " in wordnet");
		// alert( "Request failed: " + textStatus );
		// alert(xhr.responseText);
		// alert(xhr.status);
		// alert(thrownError);
	});

	/*$.ajax({
		type: 'GET',
		url: 'http://www.blogoola.com/data/destinations.json',
		async: false,
		jsonpCallback: 'jsonCallback',
		contentType: "application/json",
		dataType: 'jsonp',
		success: function(data)
		{
			alert(JSON.stringify(data));
			console.log(json);
		},
		error: function(e)
		{
		   alert(e.message);
		}});

	Works with $.get too!

	alert('http://wordnet-online.freedicts.com/ajax/' + word)
	url = 'http://wordnet-online.freedicts.com/ajax/' + word
	$.get(url, {q:word}, function(data){
	   $('#panel3 p').html(data);
	   alert(url)});*/

	$('#panel3 first').html("false");
}

// $('#googleenglish').click(function(){});
function googleenglish_search(){
	// var word = $('#queryword').html();
    // word = word.replace(/\ /g, "_");
    var word = get_word();
	//var curl = getUrl(word);
    // alert("googleenglish: " + word);

	var curl = '../dict/Google2/' + word.substr(0, 1) + '/' + word + '.json';
	var script = document.createElement('script');
	script.setAttribute('src', curl);
	document.getElementsByTagName('head')[0].appendChild(script);
	script.onload = function () {
		// alert(dict);
		var content = process_primary(dict4.primaries);
		var webdef = process_primary(dict4.webDefinitions);
		//$('#panel p').html(content + webdef);
		document.getElementById("panel4").innerHTML = content + webdef;
		changeSound();
		loadPlayer();
	}
	//translate(word);
}

$('#likes').click(function () {
	var catid;
	catid = $(this).attr("data-catid");
	// alert("I am an alert box!");
	$.get('/rango/like_category/', {
		category_id : catid
	}, function (data) {
		$('#like_count').html(data);
		$('#likes').hide();
	});
});

$('#suggestion').keyup(function () {
	var query;
	query = $(this).val();
	$.get('/rango/suggest_category/', {
		suggestion : query
	}, function (data) {
		$('#cats').html(data);
	});
});