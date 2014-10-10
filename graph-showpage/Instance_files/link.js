/*!
 *  link.js - v1
 *  Project: Xlore
 *  Description: JS for too much content in table hiding and showing in lv4 page.
 *  Author:  LMY
 */

$(document).ready(function() {
	var innerlink = function(table) {
		var limit = 8;
		$innerTable = $(table);
		$rows = $innerTable.find(' td:odd');
		$rows.css("text-align","left");
		$rows.css("padding-left","20px");
		$rows.each(function(i, col) {
			var innerArray = $(col).children();
			if (innerArray.length > limit) {

				/*	$button = $('<div class="clearfix" ><button class="btn btn-alt btn-mini btn-more clearfix" position:absolute;right:0;bottom:0>more</button></div>');
				$elem = $('<td></td>');
				$elem.append(innerArray.slice(0, 8));
				$elem.append($button);
				$elem.insertBefore($(col));
				$(this).parent().find('td')[2].remove();
				$elem.find("div").click(function() {
					if ($(this).find('button').hasClass('btn-more')) {
						$(this).parent().append(innerArray.slice(8));
						$(this).find('button').removeClass('btn-more').addClass('btn-less').text('less');
					} else {
						$(this).parent().children("a").slice(8).remove();
						$(this).find('button').removeClass('btn-less').addClass('btn-more').text('more');
					}
				});*/

				$img = $('<div class="clearfix"><a class="btn btn-alt btn-mini" style="background: transparent" href="javascript:void(0)"><i class="link-more"></i></a></div>');
				$elem = $('<td></td>');
				$elem.css("text-align","left");
				$elem.css("padding-left","20px");
				$elem.append(innerArray.slice(0, limit));
				$elem.append($img);
				$elem.insertBefore($(col));
				$(this).parent().find('td')[2].remove();
				$elem.find("div").click(function() {
					if ($(this).find('i').hasClass('link-more')) {
						$(this).parent().append(innerArray.slice(limit));
						$(this).find('i').removeClass('link-more').addClass('link-less');
					} else {
						$(this).parent().children("a").slice(8).remove();
						$(this).find('i').removeClass('link-less').addClass('link-more');
					}
				});
			}
		});
	};

	var outerlink = function() {
		var links = $('#outer-list').children();
		$('#outer-list').children().remove();
		$('#outer-list').text("");
		$list = $('#outer-list');
		links.each(function(i, item) {
			$item = $('<li></li>');
			$item.append(item);
			$item.appendTo($list);
		});
	};

	$('.inner-table').each(function(){
		innerlink(this);
	});

	outerlink();

});

