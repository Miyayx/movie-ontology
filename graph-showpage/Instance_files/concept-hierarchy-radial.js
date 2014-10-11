/*
 *  concept-hierarchy - v2
 *  Project: Xlore
 *  Description: JS plugin based on D3.js to implement visualization of a concept hierarchy image.
 *  In this image, there is a center concept word with superclass and subclass words around it. 
 *  The nodes arrange as a circle.
 *  Author:  LMY
 *  Include d3.js (http://d3js.org/) A JavaScript library for manipulating documents based on data.
 *  Include tinybox.js  A JavaScript library for pop-up box. 
 */

var conceptGraph = function(param) {
	//param = {action:"" ,json:"",chart:""}
	var chart = param.chart;
	
	//Check languish of pages
	var lan = (/.*[\u4e00-\u9fa5]+.*$/.test($('.nav li a').text()))?"ch":"en";

	var diameter = 680,
	r = diameter / 2;

	var w = 600,
	h = 500,
	i = 0

	var nodeNum = 0;

	var rectParam = {
		"rx": 5,
		"ry": 8,
		"offsetx": 20,
		"offsety": 10
	};
	
	/**
	 * Choose label text. If languish is Chinese, prefer label.ch. 
	 * If languish is English, prefer label.en
	 * @param label
	 * @returns
	 */
	function label(label){
		if(lan=="ch"){
			if(label.ch.length>0)
				return label.ch;
			else return label.en;
		}else{
			if(label.en.length>0)
				return label.en;
			else return label.ch;
		}
	}

	/**
	 * Convert the format of json
	 * @param json  The original json
	 * @param issuper  If is superclass part
	 * @returns {Array}
	 */
   function convertJson(json, issuper) {
		var children = new Array();
		if (issuper) {
			json.forEach(function(item) {
				var newItem = new Object();
				newItem.level = "super";
				newItem.uri = item.uri;
				if (label(item.label).length == 0) return;
				newItem.label = label(item.label);
				if (item.super) {
					newItem.children = convertJson(item.super, issuper);
				}
				nodeNum++;
				children.push(newItem);
			});
		} else {
			json.forEach(function(item) {
				var newItem = new Object();
				newItem.level = "sub";	
				newItem.uri = item.uri;
				if (label(item.label).length == 0) return;
				newItem.label = label(item.label);
				if (item.sub) {
					newItem.children = convertJson(item.sub, issuper);
				}
				nodeNum++;
				children.push(newItem);
			});
		}
		return children;
	}

	var tree = d3.layout.tree().sort(null).size([360, r - 100]).children(function(d) {
		return d.children ? d.children: d.super ? d.super: d.sub;
	});

	var svg = d3.select(chart).append("svg:svg").attr("width", diameter).attr("height", diameter).append("svg:g").attr("transform", "translate(" + (r + 30) + "," + r + ")");

	var start = function(json) {

		var newjson = new Object();
		newjson.level = "center";
		newjson.label = label(json.label);

		newjson.children = new Array();
		if(json.super.length > 0){
			newjson.children[0] = new Object();
			newjson.children[0].children = convertJson(json.super, true);
			newjson.children[0].label = lan=='ch'?"父概念":"SuperClass";
			newjson.children[0].level = "super-cate";
		}
		if(json.sub.length > 0){
			newjson.children[1] = new Object();
			newjson.children[1].children = convertJson(json.sub, false);
			newjson.children[1].label = lan=='ch'?"子概念":"SubClass";
			newjson.children[1].level = "sub-cate";
		}
		update(newjson);
	};

	function update(source, issuper) {

		var nodes = tree.nodes(source);
		var links = tree.links(nodes);

		//update the links
		var linkGroup = svg.selectAll("g.link").data(links).enter().append("line").attr("class", function(d) {
			return d.target.level == "super" ? "super-link": "sub-link";
		}).attr("x1", function(d) {
			return xs(d.source);
		}).attr("y1", function(d) {
			return ys(d.source);
		}).attr("x2", function(d) {
			return xs(d.target);
		}).attr("y2", function(d) {
			return ys(d.target);
		});

		//Update the nodes
		var nodeGroup = svg.selectAll("g.none").data(nodes).enter().append("svg:g").attr("class", function(d) {
			if (d.level == "sub-cate") return "sub-cate";
			else if (d.level == "super-cate") return "super-cate";
			else return "node";
		}).on("click", function(d) {//click effect
		if(d.depth == 0){
			TINY.box.hide();
		}else{
			window.location.href =encodeURI("sigInfo.action?uri="+d.uri);
		}
	});

		nodeGroup.append("svg:rect").attr("rx", rectParam.rx).attr("ry", rectParam.ry).attr("class", function(d) {
			if (d.level == "center") return "center-node";
			else if (d.level == "super") return "super-node";
			else if (d.level == "sub") return "sub-node";
			//return "translate(" +d.x+","+ d.y + ")";
		});

		var textGroup = nodeGroup.append("text").attr("text-anchor", function(d) {
			return "middle";
		}).attr("dy", ".31em").attr("transform", function(d, i) {
			return "translate(" + xs(d) + "," + ys(d) + ")";
		}).text(function(d) {
			return d.label;
		});

		//After labels have been drawn, get their size then decide the size of rectangle.
		nodeGroup.each(function(d, i) {
			d.textWidth = d3.select(this).select("text").node().getBBox().width;
			d.textHeight = d3.select(this).select("text").node().getBBox().height;
		});

		nodeGroup.selectAll("rect").attr("width", function(d) {
			return d.textWidth + rectParam.offsetx;
		}).attr("height", function(d) {
			return d.textHeight + rectParam.offsety;
		}).attr("transform", function(d) {
			return "translate(" + (xs(d) - d.textWidth / 2 - rectParam.offsetx / 2) + "," + (ys(d) - d.textHeight / 2 - rectParam.offsety / 2) + ")";
		});

		function xs(d) {
			return d.y * Math.cos((d.x + 35 * nodeNum) / 180 * Math.PI);
		}
		function ys(d) {
			return d.y * Math.sin((d.x + 35 * nodeNum) / 180 * Math.PI);
		}
	}

	//Begin....
	if (param.action) {
		d3.json(action, function(json) {
			start(json);
		});
	} else {
		if (typeof(json) == "string") json = eval('(' + param.json + ')');
		start(json);
	}
};

