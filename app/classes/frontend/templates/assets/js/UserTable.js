// User Information tabel
// Add, Delete, and Edit Users
$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip();
	var actions = $("table td:last-child").html();
	// Append table with add row form on add new button click
    $(".add-new").click(async function(){
		$(this).attr("disabled", "disabled");
		var index = $("table tbody tr:last-child").index();
		const req = await fetch("/admin/users/get_roles");
		var response = await req.json()
			.then(data => {
				roles = data.roles
			});
		console.log(roles);
        var row = '<tr>' +
            '<td><input name="user_firstname" type="text" class="form-control" name="UserFirst" id="UserFirst"></td>' +
            '<td><input name="user_lastname" type="text" class="form-control" name="UserLast" id="UserLast"></td>' +
            '<td><input name="user_email" type="text" class="form-control" name="UserEmail" id="UserEmail"></td>' +
            '<td><input name="user_password" type="text" class="form-control" name="UserPassword" id="UserPassword"></td>' +
            '<td><input name="type" type="text" class="form-control" name="UserType" id="UserType"></td>' +
			'<td>' + actions + '</td>' +
        '</tr>';
    	$("table").append(row);		
		$("table tbody tr").eq(index + 1).find(".add, .edit").toggle();
        $('[data-toggle="tooltip"]').tooltip();
    });
    
	// Add row on add button click
	$(document).on("click", ".add", function(){
		var empty = false;
		var input = $(this).parents("tr").find('input[type="text"]');
        input.each(function(){
			if(!$(this).val()){
				$(this).addClass("error");
				empty = true;
			} else{
                $(this).removeClass("error");
            }
		});
		$(this).parents("tr").find(".error").first().focus();
		if(!empty){
			input.each(function(){
				$(this).parent("td").html($(this).val());
			});			
			$(this).parents("tr").find(".add, .edit").toggle();
			$(".add-new").removeAttr("disabled");
		}		
    });
	// Edit row on edit button click
	$(document).on("click", ".edit", function(){		
        $(this).parents("tr").find("td:not(:last-child)").each(function(){
			$(this).html('<input type="text" class="form-control" value="' + $(this).text() + '">');
		});		
		$(this).parents("tr").find(".add, .edit").toggle();
		$(".add-new").attr("disabled", "disabled");
    });
	// Delete row on delete button click
	$(document).on("click", ".delete", function(){
        $(this).parents("tr").remove();
		$(".add-new").removeAttr("disabled");
    });
});
