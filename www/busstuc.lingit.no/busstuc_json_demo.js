function process_answer(data) {
    $('#tuc_output').html(data.answer);
    $('#tuc_error').html(data.answer);
}

$(document).ready(function () {
    $("#tuc_form").submit(function (event) {
	$.ajax({
	    url: $(this).attr('action'),
	    dataType: 'json',
	    type: 'GET',
	    data: {question: $(this).children('input[name=question]').val()},
	    success: process_answer
	});
	
	return false;
    });
});
