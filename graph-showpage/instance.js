$(function() {

	var initSearchBtn = function() {
		$('#search-btn').click(
		function() {
			var jsType = $('#search-type').text();
			var jsInfo = $('#search-info').val();
			var origin = document.location.origin;

			$.get(origin+"/query?query=" + jsInfo, function(data) {
				freshPage(data);
			});
		});

		$("#search-info").keypress(
		function(e) {
			if (e.which == 13 && !e.shiftKey) {
                e.preventDefault();
			  //var jsType = $('#search-type').text();
			  jsInfo = $('#search-info').val();
			  origin = document.location.origin;

			  $.get(origin+"/query?query=" + jsInfo, function(data) {
			  	freshPage(data);
				
			  });
			}
		});

		
	};

	var freshPage = function(data) {
        $('#search-info').val("");
        legends = ["Title","type","Summary","Infoboxes","Images","FullText"];

		$('#main-page').empty();
		$article = $('<article class="blue data-block"></article>');
		$header = $('<header><h2 class="name">' + '实例查询' + '</h2></br></br></header>');	
		
		var datalen = 0
		for (var k in data ) datalen ++;
					
		if (datalen>1 && ('gtype' in data))
		{	
			if (data['gtype']=='instance')
			{
				$header.appendTo($article);
				for (var i in legends){
					var key = legends[i];
					if (key == "Title"){
						$section = $('<section class="paragraph data-block"><legend>' + key + '</legend><div><p>' + data[key] + '</p></div></section>');
						if ("FirstImage" in data){
						  //$image = $('<a class="thumbnail" href="'+data["FirstImage"]+'">');
						  //$section.append($image);
						  delete data["FirstImage"];
						}

						$section.appendTo($article);

					} else if (key == "Infoboxes"){

						$section = $('<section class="paragraph data-block"><legend>' + key + '</legend></section>'); 
						$table = $('<div class="clearfix"><table class="table table-condense table-striped span8 offset0"></table></div>');
						$thead = $('<thead><tr><th style="width:30%"></th><th style="width:70%"></th></tr></thead>');
						$tbody = $('<tbody></tbody>');

						if ("alias" in data[key]){
							k = "alias";
							items = [];
							for (var i = 0; i < data[key][k].length; i++){
								item = data[key][k][i];
								items.push(item);
							}
							$tr = $('<tr><td>' + k + '</td><td>' + items.join() + '</td></tr>');
							$tbody.append($tr);
							delete data[key]["alias"];
						}
						for (k in data[key]) {
							items = [];
							for (var i = 0; i < data[key][k].length; i++){
								item = data[key][k][i];
								if(typeof(item) === "string"){
									items.push(item);
								}else if("name" in item ){
									if ("id" in item){
										items.push("<a data-url=" + item["id"]+" href='javascript:void(0)'>" + item["name"]+"</a>")
									}
									else{
										items.push(item["name"]);
									}
								}else{
									items.push(item);
								}
							}
							$tr = $('<tr><td>' + k + '</td><td>' + items.join() + '</td></tr>');
							$tbody.append($tr);
						}

						$table.find("table").append($thead);
						$table.find('table').append($tbody);
						$section.append($table);
						$section.appendTo($article);

					}else if(key == "Images"){
					/*
						$section = $('<section class="paragraph data-block"><legend>' + key + '</legend></section>');
						$ul = $('<ul class="thumbnails row-fluid"></ul>');
						for (j in data[key]) {
							img = data[key][j];
							$li = $('<li class="span2" style="margin-left:30px"><a class="thumbnail" href="' + img + '"><img src="' + img + '"></a></li>');
							$ul.append($li);
						}
						$section.append($ul);
						$section.appendTo($article);*/

					}else if(key == "type"){

						types = Array();
						for (var i = 0; i < data[key].length; i++){
							types.push(data[key][i]["name"]);
						}

						$section = $('<section class="paragraph data-block"><legend>' + "Type" + '</legend><div><p>' + types.join() + '</p></div></section>');
						$section.appendTo($article);

					}else{
						$section = $('<section class="paragraph data-block"><legend>' + key + '</legend><div><p>' + data[key] + '</p></div></section>');
						$section.appendTo($article);					
					}				
					delete data[key];
				}
			}
			else if(data['gtype']=='semQuery'){
				$header = $('<header><h2 class="name">' + '联合查询' + '</h2></br></br></header>');
				$header.appendTo($article);
				$section = $('<section class="paragraph data-block"><legend>' + data['Title'] + '</legend></section>'); 
				$table = $('<div class="clearfix"><table style="table-layout:fixed;" class="table table-condense table-striped span8 offset0"></table></div>');
				//$thead = $('<thead><tr><th style="width:25%"></th><th style="width:25%"></th></tr></thead>');
				$tbody = $('<tbody></tbody>');
				
				for (var j = 0; j < data['results'].length; j++ )
				{			
					var elems = data['results'][j];
					if (elems.length>0)
					{
						
						items = [];
						items.push('<tr><td>');
						//items.push(elems[0]);
						item = elems[0]
						if(typeof(elems[0]) === "string"){
							items.push(item["name"]);
						}else if("name" in item ){
							if ("id" in item){
								items.push("<a data-url=" + item["id"]+" href='javascript:void(0)'>" + item["name"]+"</a>")
							}
							else{
								items.push(item["name"]);
							}
						}else{
							items.push(item["name"]);
						}

						for (var i = 1; i < elems.length; i++ ){
							
							items.push('</td><td>');
							
							items.push(elems[i]);
						}
						items.push('</td></tr>');
						$tr = $(items.join().replace(/,/g,''));
						$tbody.append($tr);
					}					
				}				
				delete data["results"];
				delete data['Title'];
				//$table.find("table").append($thead);
				$table.find('table').append($tbody);
				$section.append($table);
				$section.appendTo($article);
			}

			delete data['gtype'];			
		}
		
        for (key in data){
			$section = $('<section class="paragraph data-block"><legend>' + key + '</legend><div><p>' + data[key] + '</p></div></section>');
			$section.appendTo($article);
        }

		$('#main-page').append($article);
		$("a").click(
			function() {
			//var jsType = $('#search-type').text();
			//var jsInfo = $('#search-info').val();
			var origin = document.location.origin;
			var uri = $(this).attr('data-url');

			$.get(origin+"/query?uri=" + uri, function(data) {
				freshPage(data);
			});
		});
	}

	initSearchBtn();
});

