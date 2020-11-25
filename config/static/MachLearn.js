$(document).ready(function(){

// для удачных
    $("#select_form").change(function(){
        if (($("#BP_names_list_good_bad :selected").val() != "") && ($("#mode_choice_good_bad :selected").val() != "")) {
            $("#show_table_button").prop("disabled", false);
        }
    });
	

    $("#select_form").on("submit", function(event){

        event.preventDefault();
        $("#show_table_button").prop("disabled", true)
        var $form = $(this);
        var url = $form.attr("action");

        $("#table_div").load(
            url,
            $("#select_form").serialize(),
            function(){
				if ($("#hidden_database_name_input").val() == $("#BP_names_list_good_bad").val()){
					$("#cases_from_keyboard").attr('checked', true);
				}
				$("#cases_from_keyboard").click(function(event){
					var $self = $(this);
					$("#add_cases_div").prop("hidden", false)
					if ($self.is(" :checked")) {
						$("#add_cases_div").load(
							"/MachLearn/precedents_extraction_good_bad_input",
							$("#select_form").serialize(),
							function() {
								$("#use_weights").on("change", function(){
									if ($("#use_weights").is(" :checked"))
										$("#field_to_remember_checkbox").val("on");
									else
										$("#field_to_remember_checkbox").val("off")
								})
							})
					}
	
				});
			}
		)

    });
	
	$(document).on("submit", "#classification_form", function(event){
		event.preventDefault();
		$("#answer_of_classif").prop("hidden", false)
		$("#add_case_button").prop("disabled", true)
		$("#add_cases_table td").prop("contenteditable", false);
		remember_cases();
		var $form = $(this);
		var url = $form.attr("action");
		$("#answer_of_classif").load(
			url,
			$("#classification_form").serialize()
		)
		$("#field_to_remember_cases").val("");
	});
	
    $("#BP_names_list_good_bad").on("change", function(){
		if ($("#hidden_database_name_input").val() != undefined){
			$("#add_cases_div").prop("hidden", true)
			$("#cases_from_keyboard").attr("checked", false);
		}
	});	



	$(document).on("submit", "#add_g_b_cases_form", function(event){
		event.preventDefault();
		remember_good_cases_id();
		
		var $form = $(this);
		
		var url = $form.attr("action");
		$.get(url, $form.serialize(), function(response){alert(response)});
		
		$("#answer_of_classif").prop("hidden", true);
	});
	
	
	
	// для параметрич--------------------------------------------------------------------------------------------------
	$("#select_form_param").change(function(){
        if (($("#BP_names_list_param :selected").val() != "") && ($("#mode_choice_param :selected").val() != "")) {
            $("#show_table_param_button").prop("disabled", false);
        }
    });
	
	$("#select_form_param").on("submit", function(event){

        event.preventDefault();
        $("#show_table_param_button").prop("disabled", true)
        var $form = $(this);
        var url = $form.attr("action");

        $("#table_div_param").load(
            url,
            $("#select_form_param").serialize(),
            function(){
				if ($("#hidden_database_name_input_param").val() == $("#BP_names_list_param").val()){
					$("#cases_from_keyboard_param").attr("checked", true);
				}
				
				$("#cases_from_keyboard_param").click(function(event){
					var $self = $(this);
					$("#add_cases_div_param").prop("hidden", false)
					$("#add_cases_from_file_div_param").prop("hidden", true)
					if ($self.is(" :checked")){
						$("#add_cases_div_param").load(
							"/MachLearn/precedents_extraction_param_input",
							$("#select_form_param").serialize(),
							function(){
								$("#use_weights_param").on("change", function(){
									if ($("#use_weights_param").is(" :checked"))
										$("#field_to_remember_checkbox_param").val("on");
									else
										$("#field_to_remember_checkbox_param").val("off");
								})
							})
					}});
				
				$("#cases_from_file_param").click(function(event){
					$("#add_cases_from_file_div_param").prop("hidden", false);
					$("#add_cases_div_param").prop("hidden", true);
				});
				
				$("#load_cases_from_file_button").click(function(event){
					if($("#cases_file").val() != ""){
						$("#add_cases_div_param").prop("hidden", false);
						$("#add_cases_div_param").load(
							"/MachLearn/precedents_extraction_param_input_file",
							$("#add_cases_from_file, #select_form_param").serialize(),
							function(){
								alert('uytredf');
							})
					}
					else
						alert("Файл не выбран!");
				});

			}
		)});
	
	$(document).on("submit", "#classification_form_param", function(event){
		event.preventDefault();
		$("#answer_of_classif_param").prop("hidden", false)
		$("#add_case_button_param").prop("disabled", true)
		$("#add_cases_table_param td").prop("contenteditable", false);
		remember_cases();
		var $form = $(this);
		var url = $form.attr("action");
		$("#answer_of_classif_param").load(
			url,
			$("#classification_form_param").serialize()
		)
		$("#field_to_remember_cases_param").val("");
	});
	
    $("#BP_names_list_param").on("change", function(){
		if ($("#hidden_database_name_input_param").val() != undefined){
			$("#add_cases_div_param").prop("hidden", true)
			$("#add_cases_from_file_div_param").prop("hidden", true)
			$("#cases_from_keyboard_param").attr("checked", false);
			$("#cases_from_file_param").attr("checked", false);
		}
	});

	// для кросс-валидации--------------------------------------------------------------------------------------------------
	$("#select_form_cross_validation").change(function(){
        if (($("#BP_names_list_cross_validation :selected").val() != "") && ($("#mode_choice_cross_validation :selected").val() != "")) {
            $("#show_table_cross_validation_button").prop("disabled", false);
        }
    });
	
	$("#select_form_cross_validation").on("submit", function(event){

        event.preventDefault();
        $("#show_table_cross_validation_button").prop("disabled", true)
        var $form = $(this);
        var url = $form.attr("action");

        $("#table_div_cross_validation").load(
            url,
            $("#select_form_cross_validation").serialize()
		)
    });
	
	$(document).on("submit", "#cross_validation_form", function(event){
		event.preventDefault();

		var $form = $(this);
		var url = $form.attr("action");
		$("#answer_of_cross_validation").load(
			url,
			$("#cross_validation_form").serialize()
		)
	});

});