$(document).ready(function() {
});

var curr_show_example = true;

var get_all_example_uls = function(){
    var results = [];
    var eles = document.getElementsByTagName("ul");
    for(var i in eles){
        if(eles[i].className == "entries_example"){
        results.push(eles[i]);
        }
    }
    return results;
}

var hide_example = function(){
	var tog = $("#toggle_example");
	//alert(tog.innerHTML);
	tog.innerHTML = "+ Show Examples";
	$(".example").hide();
	curr_show_example = false;
	//alert("hide_example");
	//set_cookie(example_key,0,example_cookie_days);
}

var show_example = function(){
	var tog = $("toggle_example");
	tog.innerHTML = "- Hide Examples";
	$(".example").show();
	curr_show_example = true;
	alert("show_example");
	//set_cookie(example_key,1,example_cookie_days);
}

var toggle_example = function(){
	alert("toggle_example");
	if(curr_show_example){hide_example();}
	else{show_example();}
}

$("#toggle_example").click(function() {
	$('.example').toggleClass('hide_Style');
	//alert("(\"#toggle_example\").click");
	//var togtext = $(this).text();
	//alert(togtext);
	if(curr_show_example){
		curr_show_example = false;
		//alert($(this).attr)
		//$(this).innerHTML = "+ Show Examples";
		$(this).text("+ Show Examples");
		
	}
	else{
		curr_show_example = true;
		//$(this).innerHTML = "- Hide Examples";
		$(this).text("- Hide Examples");
	}
});

$("#toggle_example").mouseover(function() {
	$('.none_class_just_example').toggleClass('bold');
});

$('#toggle_example').bind('mouseenter mouseleave', function(){
	$(this).toggleClass('bold');
});