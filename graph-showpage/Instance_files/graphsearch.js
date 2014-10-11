/*!
 *  graphsearch.js - v1
 *  Project: Xlore
 *  Description: Visualization button click effect. Send the uri of label to server 
 *               and get a json data for visualization. Decide the type of image according to 
 *               the type of json.(concept or instance)
 *  Author:  LMY
 *  Include tinybox.js  A JavaScript library for pop-up box
 */

/**
 * 
 * @param uri uri of the center label
 */
function createGraphBox(uri) {
	TINY.box.show({
		boxid: 'graphbox',
		width: 700,
		height: 640,
		animate: true,
		url: 'json/graph.action?graphuri=' + uri,//Use ajax in tinybox
		//			url:'json/graph.action',
		openjs: function() {
			openJS();
		}
	});

	var openJS = function() {
		
		/**
		 * if there is no json data or there is error in server.
		 */
		function noData(){
			$('#graphbox').animate({width:'100px',height:'100px'},500);
			$('.tcontent').append($('<p  style="font-size:20px" class="text-warning">暂无数据</p>'));
			$('.tcontent').css({'text-align': 'center', 'vertical-align': 'middle','margin-top':'35px'});
		};
		
		json = TINY.box.data();
		if (typeof(json) == "string" && json.length < 4) {//Check if there is data for show
			noData();
			return;
		}
		while (typeof(json) == "string")
		json = eval("(" + json + ")");
		
		if(json.type == "concept"&&json.label.ch=="null"&&json.label.en=="null"){
			//Check if there is data for show	
			noData();
			return;
		}
			
		if (json.type == "concept") {
			//			TINY.box.size(500,500);
			$('.tcontent').attr('id', 'concept-chart').text("");
			//conceptGraph('/Lore4/conceptGraphJson.action','#concept-chart');
			conceptGraph({
				json: json,
				chart: '#concept-chart'
			});
		}
		if (json.type == "instance") {
			//	TINY.box.size(750,700);
			$('.tcontent').attr('id', 'instance-chart').text("");
			//		instanceGraph({action:'/Lore4/instanceGraphJson.action',chart:'#instance-chart'});
			instanceGraph({
				json: json,
				chart: '#instance-chart'
			});
		}
	};
};

/*var createConceptGraphBox = function() {

	TINY.box.show({
		boxid: 'graphbox',
		width: 500,
		height: 500,
		animate: true,
		url: '/Lore4/conceptGraphJson.action',
		openjs: function() {
			openJS();
		}
	});

	var openJS = function() {
		$('.tcontent').attr('id', 'concept-chart').text("");
		//conceptGraph('/Lore4/conceptGraphJson.action','#concept-chart');
		conceptGraph({
			json: TINY.box.data(),
			chart: '#concept-chart'
		});
	};
};

var createInstanceGraphBox = function() {

	TINY.box.show({
		boxid: 'graphbox',
		width: 750,
		height: 700,
		animate: true,
		url: '/Lore4/instanceGraphJson.action',
		openjs: function() {
			openJS();
		}
	});

	var openJS = function() {
		$('.tcontent').attr('id', 'instance-chart').text("");
		//		instanceGraph({action:'/Lore4/instanceGraphJson.action',chart:'#instance-chart'});
		instanceGraph({
			json: TINY.box.data(),
			chart: '#instance-chart'
		});
	};
};*/

//if (window.location.href.split("searchGraph").length > 1	){
//		$.getJSON('/Lore4/instanceGraphAction3.action',function(data){			
//			alert(data.toString());
//		});
//	createConceptGraphBox();
//	createInstanceGraphBox();
//	createGraphBox();
//		}

$(document).ready(function() {
	//In four-level page,when click visualization
	$('#graph-show').click(function() {
		var href = window.location.href;
		var end = href.indexOf("#") == - 1 ? href.length: href.indexOf("#");
		var uri =  href.substring(href.indexOf("uri=") + 4, end);
		createGraphBox(uri);
	});
	
	//In three-level page,when click visualization
	$('.vis-btn').click(function() {
		var href = $(this).prev().attr('href');
		var uri = href.substring(href.indexOf("uri=") + 4);
		createGraphBox(uri);
	});
	
});

