$(document).ready(function(){
	loadPlayer();
});

function loadPlayer(){
	$('[id=playpause]').each(function(n){
		// console.log("add click: ", $(this));
		$(this).click(function(){
			// audio = document.getElementById('myaudio');
			// document.getElementsByClassName('d');
			// document.getElementsByTagName('p');//获取页面中所有的标签为p的元素集合
			// document.getElementsByName('user');//获取页面中所有的name为user的元素集合
			// alert($(this).prop("tagName"))
			// alert($('.sound').attr('id'))
			// alert($(this).next().attr('id'))
			nextTag = $(this).next();
			// nextTagName = nextTag.prop("tagName");
			// alert(nextTagName);
			// alert(nextTag.attr('id'));
			audio = nextTag[0];
			// console.log(audio);
			// var it = $(this)
			// alert($(this).attr("class"))
			// audio = $(this).parent()
			// console.log($(this).html());
			if (audio.paused || audio.ended) {
				// console.log("click: allow to play!");
				audio.play();
			} else {
				// console.log("click: not allow to play!");
				audio.pause();
			}
		})
	});

	$("audio").each(function(i){
		// console.log("addEventListener: " + $(this).html())
		$(this)[0].addEventListener("play", function() {
			var btn = $(this).prev()
			// console.log("addPlayEventListener: ", btn);
			updateButtons(btn, true);
		}, false);
		$(this)[0].addEventListener("playing", function() {
			var btn = $(this).prev()
			// console.log("addPlayingEventListener: ", btn);
			updateButtons(btn, true);
		}, false);
		$(this)[0].addEventListener("ended", function() {
			var btn = $(this).prev()
			// console.log("addEndedingEventListener: ", btn);
			updateButtons(btn, false);
		}, false);		
	});	
}

function updateButtons(btn, playing) {
	// if(playing === undefined) {
		// playing = !this.status.paused;
	// } else {
		// this.status.paused = !playing;
	// }
	// Apply the state classes. (For the useStateClassSkin:true option)
	if(playing) {
		// this.addClass('jp-state-playing');
		btn.addClass('jp-state-playing');
	} else {
		// this.removeClass('jp-state-playing');
		btn.removeClass('jp-state-playing');
	}
	/*if(!this.status.noFullWindow && this.options.fullWindow) {
		this.addStateClass('fullScreen');
	} else {
		this.removeStateClass('fullScreen');
	}
	if(this.options.loop) {
		this.addStateClass('looped');
	} else {
		this.removeStateClass('looped');
	}
	// Toggle the GUI element pairs. (For the useStateClassSkin:false option)
	if(this.css.jq.play.length && this.css.jq.pause.length) {
		if(playing) {
			this.css.jq.play.hide();
			this.css.jq.pause.show();
		} else {
			this.css.jq.play.show();
			this.css.jq.pause.hide();
		}
	}
	if(this.css.jq.restoreScreen.length && this.css.jq.fullScreen.length) {
		if(this.status.noFullWindow) {
			this.css.jq.fullScreen.hide();
			this.css.jq.restoreScreen.hide();
		} else if(this.options.fullWindow) {
			this.css.jq.fullScreen.hide();
			this.css.jq.restoreScreen.show();
		} else {
			this.css.jq.fullScreen.show();
			this.css.jq.restoreScreen.hide();
		}
	}
	if(this.css.jq.repeat.length && this.css.jq.repeatOff.length) {
		if(this.options.loop) {
			this.css.jq.repeat.hide();
			this.css.jq.repeatOff.show();
		} else {
			this.css.jq.repeat.show();
			this.css.jq.repeatOff.hide();
		}
	}*/
}