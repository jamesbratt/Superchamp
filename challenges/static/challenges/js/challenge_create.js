$( document ).ready(function() {
	$('#id_end_date').datepicker({
	    format: 'mm/dd/yyyy',
	});
    $('#id_target_time').timepicker({
        showInputs: false,
        showMeridian: false,
        showSeconds: true,
        defaultTime: '00:00:00',
        minuteStep: 1
      })
})