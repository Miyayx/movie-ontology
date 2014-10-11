/*!
 *  instance-graph.js - v1
 *  Project: Xlore
 *  Description: Instance Graph Visualization 
 *               JS plugin based on D3.js to implement visualization of the instance image.
 *               In this image, there is a center instance with its related items and linked items around.
 *               The nodes arrange as circle.
 *               The nodes arrange in three levels. The innermost level includes the center instance, the middle
 *               level is composed by related items. The outermost level is composed by innerlink items,which have
 *               indirect relationship with the center instance. 
 *  Author:  LMY
 *  Include d3.js (http://d3js.org/) A JavaScript library for manipulating documents based on data. 
 *  Include tinybox.js  A JavaScript library for pop-up box.
 */

var instanceGraph = function(param) {
	//param = {action:"" ,json:"",chart:""}
	var chart = param.chart;
	var idIndex = 0; // help increase id of g.node
	var defaultImage = "./img/noimage.png";
	
	var currentRoot;
	var diameter = 650,radius = diameter / 2;
	var centerX = radius,centerY = 0;
	
	NodeOptions = {
			"fontSize":"15px",
			"textAnchor":"middle"
	};
	
	TextOptions = {
			"color":"gray",
	        "fontSize":"14px",
	        "translate":"-30"
	};

	var colors = ["skyblue", "blue", "purple", "mediumpurple", "deeppink", "red", "darkorange", "green","darkgreen","#1a242f"];
//	var colors = ["#FF9900","FFFF00","#66FF00","#00FF00","#00FF99","#00FFFF",
//	              "0099ff","#0000ff","#9900ff","#ff00ff","#ff0099","#FF0000"];


	var tree = d3.layout.tree().size([360, radius - 50]).separation(function(a, b) {
		return (a.parent == b.parent ? 1: 2) / a.depth;
	}).children(function(d) { // decide where to create a new node
		if (d.categories != undefined) return d.categories;
		else if (d.children != undefined) return d.children;
		else if (d.innerlink != undefined) return d.innerlink;
		else return null;
	});

	// form of lines
	var diagonal = d3.svg.diagonal.radial().projection(function(d) {
		return [d.y, d.x / 180 * Math.PI];
	});

	//	function project(d) {
	//		var r = d.y, a = (d.x - 90) / 180 * Math.PI;
	//		return [r * Math.cos(a), r * Math.sin(a)];
	//	}
	var vis = d3.select(chart).append("svg").attr("width", diameter).attr("height", diameter).append("g").attr("transform", "translate(" + radius + "," + radius + ")");
	vis.append("svg:defs").append("svg:clipPath").attr("id", "background-clip").append("svg:circle").attr("x", - radius).attr("y", - radius).attr("r", radius);

	//vis.append("image")
	//.attr("xlink:href","../picture/background.jpg")		
	//.attr("clip-path", "url(#background-clip)")
	//.attr("x",-radius)
	//.attr("y",-radius-75)
	//.attr("width", radius*2)
	//.attr("height", radius*2+150);
	//vis.append("circle")
	//.attr("x",-radius)
	//.attr("y",-radius-75)
	//.attr("r", radius+75)
	//.attr("fill","black");
	
	if(param.action){
	d3.json(param.action, function(json) {
		currentRoot = json;
		update(currentRoot);
	});
	}else{
		if(typeof(json) == "string"){
		json = eval('('+param.json+')');
		}
		currentRoot = json;
		update(currentRoot);
	};

	function update(source) {
		var duration = d3.event && d3.event.altKey ? 5000: 500;

		//create infobox and render its color and position
		//infobox lib in infobox-bubble.js
		//	var renderInfobox = function(v,d){
		//		var infobox = createInfobox(v,d.infobox);
		//		infobox.selectAll("rect.label")
		//			.attr("fill",function(d){ return d.color; });
		//
		//		infobox.selectAll("rect.context")
		//			.attr("fill","white");
		//
		//		infobox.select("rect.background")
		//			.attr("stroke",function(d){return d.color;});
		//
		//		infobox.select("polygon")
		//			.attr("fill",function(d){return d.color;})
		//			.attr("fill-opacity",0.5);
		//
		//	infobox
		//		.attr("transform",function(d){
		//			return (d.x > 90)&&(d.x < 270) ? "matrix(1 0 0 1 "+(30+d.r*1.2)+" "+(-captionH)+")" : "matrix(1 0 0 -1 "+(30+d.r*1.2)+" "+captionH+")"; 
		//		});
		//	infobox
		//		.selectAll("text")
		//		.attr("transform", function(d) {
		//			return (d.x > 90)&&(d.x < 270) ? null : "rotate(180)" ;  });
		//	infobox
		//		.selectAll("tspan")
		//		.attr("transform", function(d) {
		//			return (d.x > 90)&&(d.x < 270) ? null : "rotate(180)"  });
		//
		//		infobox.attr("transform",function(d){
		//			return (d.x > 90)&&(d.x < 270) ? 
		//			"translate("+(d.r*1.2+infobox_p_width)+","+(-1*captionH)+")" //x:magnifying circle's radius and infobox's pointer's width
		//			: "rotate(180) translate("
		//			+(-1*(d3.select("rect.background").node().width.baseVal.value+infobox_p_width+d.r*1.2))
		//			//x: infobox's width+infobox's pointer's width+magnifying circle's radius
		//			+","+(-1*captionH)+")";});
		//
		//		infobox.select("polygon")
		//			.attr("transform",function(d){ //if the degree is between 90 and 270, reverse the triangle and adjust position 
		//				return	(d.x > 90)&&(d.x < 270) ? "matrix(-1 0 0 1 "+
		//				(d3.select("rect.background").node().width.baseVal.value)
		//				+" 0)":null; })
		//	}
		// Compute the new tree layout.
		var nodes = tree.nodes(source);

		// Update the nodes
		var node = vis.selectAll("g.node").data(nodes, function(d) {
			return d.id || (d.id = ++idIndex);
		}); //judge if the node is a new one based on id
		// Enter any new nodes at the parent's previous position.
		var nodeEnter = node.enter().append("svg:g").attr("class", function(d) {
			return d.category != undefined ? "category": "node";
		}).attr("transform", function(d) {
			 if (isNaN(d.x)) d.x = d.id==1? 360: 450;
			return "rotate(" + (d.x + 180) + ")translate(" + d.y + ")";
		});

		//calculate radius for every node and assign it to d.r
		node.each(function(d, i) {
			if (d.r) return;
			if (d.label == undefined) {
				d.r = 0;
			}
			else if (d.depth == 0) {
				d.r = 45;
			}
			else {
				d.r = 80 / (d.depth+1) + d.depth;
			}
		});

		//choose color for every node and assign it to d.color
		var colorIndex = 0;
		node.each(function(d, i) {
			if (d.depth == 0) d.color = "gray";
			else if (d.category != undefined) d.color = d.color ? d.color: colors[colorIndex++];
			else d.color = d.color ? d.color: colors[colorIndex];
		});

		//define clip-path so that the round image can be cut out
		var defs = nodeEnter.append("svg:defs");
		defs.append("svg:clipPath").attr("id", function(d, i) {
			d.clip_normal = "image-circle1" + d.id;
			return d.clip_normal;
		}).append("svg:circle").attr("x", function(d) {
			return ( - 1) * d.r;
		}).attr("y", function(d) {
			return ( - 1) * d.r;
		}).attr("r", function(d) {
			return d.r;
		});

		//when moveover, the image should be magnified, so the clippath should be different.
		defs.append("svg:clipPath").attr("id", function(d, i) {
			d.clip_large = "image-circle2" + d.id;
			return d.clip_large;
		}).append("svg:circle").attr("x", function(d) {
			return ( - 1) * d.r * 1.2;
		}).attr("y", function(d) {
			return ( - 1) * d.r * 1.2;
		}).attr("r", function(d) {
			return d.r * 1.2;
		});

		// append images
		nodeEnter.append("image").attr("xlink:href", function(d) {
			return d.imageurl ?d.imageurl: defaultImage;
		}).attr("clip-path", function(d, i) {
			return "url(#" + d.clip_normal + ")";
		}).attr("visibility", "hidden").attr("onload", function(d) {
			var svgImage = d3.select(this);
			var image = new Image();
			image.src = d.imageurl ? d.imageurl: defaultImage;
			image.onload = function() {
				// to get real image height and width and calculate suitable height and width for showing image
				var c = d.r * 2;
				if (image.width > image.height) {
					d.imgheight = c;
					d.imgwidth = image.width * c / image.height;
				} else {
					d.imgheight = image.height * c / image.width;
					d.imgwidth = c;
				}
				svgImage.attr("height", d.imgheight);
				svgImage.attr("width", d.imgwidth);
				svgImage.attr("x", ( - 1) * d.imgwidth / 2);
				svgImage.attr("y", ( - 1) * d.imgheight / 2);

			};
			image.onerror = function() {
				image.src = defaultImage;
			};
		}).attr("transform", function(d) {
			return "rotate(" + ( - d.x + 180) + ")";
		});

		// draw the circle boundary
		var allCircle = nodeEnter.append("circle").attr("class", "imageBorder").attr("stroke-opacity", "1e-6");
/*		.on("dblclick", function(d) {
			if (d.depth === 0) { // if it's the root node,then turn back to the prev data
				data = dataStack.pop();
				if (data) {
					currentRoot = data;
					update(currentRoot);
				}
			} else {
				d3.json("../data-infobox2.json", function(json) {
					dataStack.push(currentRoot);
					currentRoot = json;
					update(currentRoot);
				});
			}
		});*/

		d3.selectAll('g.node').each(function(d, i) {

			d3.select(this).on("click", function(d) {
/*				TINY.box.show({
					url: "infobox-table.html",
					boxid: 'infobox',
					animate: true,
					openjs: function() {
						renderInfobox(d);
					}
				});*/
				if(d.depth == 0){
					TINY.box.hide();
				}else{
				//	TINY.box.hide();
					window.location.href =encodeURI("sigInfo.action?uri="+d.uri);
				}
			}).on('mouseenter', function(d) {
				//	if(d3.select(this.parentNode).select("g.infobox").node()) // if infobox has been created
				//	return;
				if (d.isover) return; // if the mouse already over the circle
				d.isover = true; // the mouse is over the circle
				//magnify the circle
				var circle = d3.select(this).select(".imageBorder");
				circle.transition().duration(50).attr("r", function(d) {
					return d.r * 1.2;
				}).attr("fill", "white").style("fill-opacity", 0.5);

				d3.select(this).append("text").attr("transform", function(d) {
					return "rotate(" + ( - d.x + 180) + ")";
				}).attr("dy", ".31em").attr("text-anchor", NodeOptions.textAnchor).attr("font-size", NodeOptions.fontSize).attr("fill", function(d) {
					return d.color;
				}).text(function(d) {
					return d.label;
				});

				//magnify the image 
				d3.select(this).select('image').attr("clip-path", function(d, i) {
					return "url(#" + d.clip_large + ")";
				}).attr("width", function(d) {
					return d.imgwidth * 1.2;
				}).attr("height", function(d) {
					return d.imgheight * 1.2;
				}).attr("x", function(d) {
					return ( - 1) * d.imgwidth * 1.2 / 2;
				}).attr("y", function(d) {
					return ( - 1) * d.imgheight * 1.2 / 2;
				});

				this.parentNode.insertBefore(this); // bring this node and its infobox to the front
				//	 if there is infomation, draw infobox
				//	if(d.infobox == undefined)	return;
				//	renderInfobox(d3.select(this.parentNode),d);
			}).on('mouseleave', function(d, e) {

				d.isover = false; //the mouse isn't over the circle
				//recover the state 
				var circle = d3.select(this).select('.imageBorder');
				circle.transition().duration(50).attr("r", function(d) {
					return d.r;
				}).style("fill-opacity", 0);
				d3.select(this).select('text').remove();

				d3.select(this).select('image').attr("clip-path", function(d, i) {
					return "url(#" + d.clip_normal + ")";
				}).attr("width", function(d) {
					return Math.floor(d.imgwidth);
				}).attr("height", function(d) {
					return Math.floor(d.imgheight);
				}).attr("x", function(d) {
					return ( - 1) * d.imgwidth / 2;
				}).attr("y", function(d) {
					return ( - 1) * d.imgheight / 2;
				});

				// remove infobox
				//	d3.select(this.parentNode).select('g').remove();
			});
		});

		var categoryNode = vis.selectAll('g.category').append('text').attr("color", TextOptions.color).style("fill", TextOptions.color).attr("font-size", TextOptions.fontSize).text(function(d) {
			return d.category;
		}).attr("transform", function(d) {
			return (d.x > 90) && (d.x < 270) ? null: "rotate(180) translate("+TextOptions.translate+")";
		});

		//write label
		//	nodeEnter.append("text")
		//		.attr("dx", function(d) { 
		//			return (d.x > 90)&&(d.x < 270) ? d.r+5 : (-1)*d.r-5; 
		//		})
		//	.attr("dy", ".31em")
		//		.attr("text-anchor", function(d) { return (d.x > 90)&&(d.x < 270) ? "start" : "end"; })
		//		.attr("transform", function(d) {
		//			return (d.x > 90)&&(d.x < 270) ? null : "rotate(180)"; })
		//		.attr("stroke-width",1)
		//		.attr("fill-opacity","1e-6")
		//		.text(function(d) { return d.label; });
		//
		//write relationship

		//------------------------------ Update Trasition ----------------------------------//
		// Transition all nodes to their new position.
		var nodeUpdate = node.transition().duration(duration).attr("transform", function(d) {
			return "rotate(" + (d.x + 180) + ")translate(" + d.y + ")";
		});

		nodeUpdate.select("image").attr("clip-path", function(d, i) {
			return "url(#" + d.clip_normal + ")";
		}).attr("visibility", "visible");

		nodeUpdate.select("text").attr("fill", function(d) {
			return d.color;
		}).style("fill-opacity", 1);

		nodeUpdate.select("circle.imageBorder").attr("r", function(d) {
			return d.r;
		}).attr("stroke", function(d) {
			return d.color;
		}).attr("stroke-opacity", 0.5);

		//------------------------------- Transition exiting nodes ----------------------------//
		var nodeExit = node.exit().transition().duration(duration).attr("transform", function(d) {
			return "translate(" + d.x + "," + d.y + ")";
		}).remove();

		nodeExit.select("image").attr("visibility", "hidden");

		nodeExit.select("circle.imageBorder").attr("stroke-opacity", 0).attr("r", 0);

		nodeExit.select("text").style("fill-opacity", 0);
		//-------------------------- Update the links ------------------------------//
		var link = vis.selectAll("path.link").data(tree.links(nodes));

		// Initialize new links to the center.
		link.enter().insert("svg:path", "g").attr("class", "link").attr("transform", function(d) {
			return "rotate(" + ( - 90) + ")";
		}).transition().duration(duration).attr("d", function(d) {
			var o = {
				x: centerX,
				y: centerY
			};
			return diagonal({
				source: o,
				target: o
			});
		});

		// Transition links to their new position.
		link.attr("transform", function(d) {
			return "rotate(" + ( - 90) + ")";
		}).transition().duration(duration).attr("d", diagonal);

		// Transition exiting nodes to the center.
		link.exit().transition().duration(duration).attr("d", function(d) {
			var o = {
				x: centerX,
				y: centerY
			};
			return diagonal({
				source: o,
				target: o
			});
		}).remove();

		/*	var relationship = vis.selectAll("g.relationship")
			.data(tree.links(nodes));

			var relationshipEnter = relationship.enter().append("svg:g")
			.attr("class","relationship")
			.attr("transform", function(d) { return (d.target.x > 90)&&(d.target.x < 270) ?
			"rotate(" + (-90) + ")" :
			"rotate("+90+" "+d.target.x+","+d.target.y+")"; }); 

			var pathDefs = relationshipEnter.append("svg:defs");
			pathDefs.append("svg:path")
			.attr("id", function(d,i){	
			d.relationpath = "relationpath"+d.target.id;
			return d.relationpath;	})
			.attr("d",diagonal);

			relationshipEnter.append("text")
		//	.attr("text-anchor","end")
		.attr("text-anchor", function(d) { return (d.target.x > 90)&&(d.target.x < 270) ? "end" : "start"; })
		.attr("x",function(d){ return -d.target.r-5; })
		.attr("dy", ".31em")
		.attr("stroke-width",1)
		.style("font-size", "12px")
		.attr("fill-opacity","1e-6")
		.attr("fill",function(d){ return d.target.color; })
		.append("textPath")
		.attr("xlink:href", function(d){ return "#"+d.relationpath; })
		.attr("startOffset","100%")
		.attr("transform", function(d) {
		return "rotate(80)"; })
		.text( function(d){ return d.target.label; })

		relationship.selectAll("text")
		.transition()
		.duration(duration)
		.attr("fill-opacity","1");

		relationship.exit().selectAll("text")
		.transition()
		.duration(duration)
		.attr("fill-opacity","1e-6");
		relationship.exit().remove();*/
	}
};

