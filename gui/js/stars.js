// $(function(){
	// load_starts(0);
// });

function load_starts(n){
	//为星星设置hover效果
	var isClicked = false;
	var beforeClickedIndex = -1;
	var clickNum = 0; //点击同一颗星次数

	for(var i = 1; i <= n; i++) {
		$('.stars li:nth-child(' + i + ')').css('color', '#F0AD4E');
	}

	$('.stars li').hover(
		function() {
			if(!isClicked) {
				$(this).css('color', '#F0AD4E');
				var index = $(this).index();

				for(var i = 0; i <= index; i++) {
					$('.stars li:nth-child(' + i + ')').css('color', '#F0AD4E');
				}
			}
		},
		function() {
			if(!isClicked) {
				$('.stars li').css('color', '#ADADAD');
			}
		}
	);

	//星星点击事件
	$('.stars li').click(function() {
		$('.stars li').css('color', '#ADADAD');
		isClicked = true;
		var index = $(this).index();

		for(var i = 1; i <= index+1; i++) {
			$('.stars li:nth-child(' + i + ')').css('color', '#F0AD4E');
		}

		if(index == beforeClickedIndex) { //两次点击同一颗星星 该星星颜色变化
			clickNum++;
			if(clickNum % 2 == 1) {
				$('.stars li:nth-child(' + (index + 1) + ')').css('color', '#ADADAD');
			} else {
				$('.stars li:nth-child(' + (index + 1) + ')').css('color', '#F0AD4E');
			}

		} else {
			clickNum = 0;
			beforeClickedIndex = index;
		}
	});	
}