$(document).ready(function(){
	
	$("#struct_select_form").change(function(){
		if ($("#BP_names_struct :selected").val() != "") {
			$("#show_struct_button").prop("disabled", false)
		}
	});
	
	$("#struct_select_form").on("submit", function(event) {

		event.preventDefault();
		$("#show_struct_button").prop("disabled", true)
		var $form = $( this );
		var url = $form.attr( "action" );
	
		$("#struct_menu").load(
			url, 
			$("#struct_select_form").serialize()
		)

	});
	$("#situation_form").on("submit", function(event) {
		event.preventDefault();
		$("#mistake_message").attr("hidden", true);
		var $form = $( this );
		var url = $form.attr( "action" );
		
		$("#situation_ontology_form").load(
			url, 
			$("#situation_form").serialize()
		)

	});


	$('.list-group-item').each( function( index, element ){
		$(this).css("padding-left", (15 * $(this).parents('.list-group, .list-group-root').length) + 'px');
	});


	var network = null;
	var container = document.getElementById('BPnetwork');
	
	if ($('#BPOntologyStorage').data() != null)
	{
		var data = $('#BPOntologyStorage').data();
		var json_edges = data.edges;
		var json_hierarchy = data.graph;
		var nodes = new vis.DataSet();
		var edges = new vis.DataSet();
		var i = 1;
		for (var key in json_hierarchy){
			nodes.add({id: key, label: key});
			i++;
		}
		edges.add(json_edges)

		// create a network
		

		// provide the data in the vis format
		var data = {
			nodes: nodes,
			edges: edges
		};
		var options = {
			layout: {
				hierarchical: {
					direction: "UD",
					sortMethod: "directed"
				}
			},
			edges: {
				arrows: "to"
			}
		};
		// initialize your network!
		network = new vis.Network(container, data, options);

	}
	
	$('#situationUL .list-group-item').on('click', function(ev) {
		var node_from_list_item = '';
		if ($(this).children('i').length == 0)
		{
			node_from_list_item = $(this).text();
		}
		else {
			node_from_list_item = $(this).text().trim();
		}
		situation_network.selectNodes([node_from_list_item]);
		$('#current_node').text(node_from_list_item);
		$('#current_node_hidden').val(node_from_list_item);
		$('#delete_param').prop('disabled', false);
		ev.preventDefault();

		});
		var situation_network = null;
	var container = document.getElementById('Situationnetwork');
	
	if ($('#SituationOntologyStorage').data() != null)
	{
		var data = $('#SituationOntologyStorage').data();
		var json_edges = data.edges;
		var json_hierarchy = data.graph;
		var nodes = new vis.DataSet();
		var edges = new vis.DataSet();
		var i = 1;
		for (var key in json_hierarchy){
			nodes.add({id: key, label: key});
			i++;
		}
		edges.add(json_edges)

		// create a network
		

		// provide the data in the vis format
		var data = {
			nodes: nodes,
			edges: edges
		};
		var options = {
			layout: {
				hierarchical: {
					direction: "UD",
					sortMethod: "directed"
				}
			},
			edges: {
				arrows: "to"
			}
		};
		// initialize your network!
		situation_network = new vis.Network(container, data, options);

	}
	$("#node_name").change(function() {
		if ($('#node_name').val() != '' && $('#current_node').text() != 'Не выбрано')
		{
			$('#add_new_param').prop('disabled', false);
		}
		else 
		{
			$('#add_new_param').prop('disabled', true);
		}
	});
	if (situation_network != null) {
		situation_network.on('select', function (properties) {
			var nodeID = properties.nodes[0];
            if (nodeID) {
                var clickedNode = this.body.nodes[nodeID];
			}
			$('#current_node').text(clickedNode.options.label);
			$('#current_node_hidden').val(clickedNode.options.label);
			$('#delete_param').prop('disabled', false);
		});
	}
	$('#situationTable').on('dblclick', 'td', function(e)
	{
		//ловим элемент, по которому кликнули
		var t = e.target || e.srcElement;
		//получаем название тега
		var elm_name = t.tagName.toLowerCase();
		//если это инпут - ничего не делаем
		if(elm_name == 'input')	{return false;}
		var val = "";
		var code = '<input type="text" id="edit" value="'+val+'" />';
		window.buf=val;
		$(this).empty().append(code);
		$('#edit').focus();
		$('#edit').blur(function()
		{
			$(this).parent().empty().html(window.buf);
		});
	});
	
	$(window).keydown(function(event)
	{
		//ловим событие нажатия клавиши
		if(event.keyCode == 13 && document.getElementById('edit')==document.activeElement)
		{
			var ValData=$('#edit').val();
			window.buf=ValData;
			$('#edit').blur();
		}
	});
	
	$('#struct_extraction').on('click', function(){
		//alert('struct_extraction');
		
		var params = $("#situationTable thead tr th").map(function(){
			return $(this).html();
		});
		
		var values = $("#situationTable tbody tr td").map(function(){
			return $(this).html();
		});
		
		var temp = "";
		
		for (i=0; i<params.length && i<values.length; i++)
			temp = temp + params[i] + ":" + values[i] + ";";
		
		$('#situationString').val(temp);
	});
	
	// ---------структурированное извлечение--------
	$("#extraction_for_struct_form").on("submit", function(event){
		event.preventDefault();

		$("#situation_ontology_form").removeClass("in active");
		$("#result_ontology_form").addClass("in active");
		$("#situation_ontology_li").removeClass("active");
		$("#result_ontology_li").addClass("active");

		var $form = $( this );
		var url = $form.attr( "action" );
	
		$("#result_struct_extraction").load(
			url, 
			$("#extraction_for_struct_form").serialize()
		)
	});

});
		$(document).on('click', '.list-group-item', function(e) {
			$('.glyphicon', this).toggleClass('glyphicon-chevron-right').toggleClass('glyphicon-chevron-down');  
			e.preventDefault();
			
	});