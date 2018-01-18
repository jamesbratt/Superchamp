$( document ).ready(function() {    
/* initialize the calendar
     -----------------------------------------------------------------*/
    //Date for the calendar events (dummy data)
    var date = new Date()
    var d    = date.getDate(),
        m    = date.getMonth(),
        y    = date.getFullYear()
    $('#calendar').fullCalendar({
      header    : {
        left  : 'prev,next today',
        center: 'title',
        right : 'month,agendaWeek,agendaDay'
      },
      buttonText: {
        today: 'today',
        month: 'month',
        week : 'week',
        day  : 'day'
      },
      events: function(start, end, timezone, callback) {
    	  console.log(start.format());
    	  console.log(end.format());
    	  console.log(timezone);
    
          $.ajax({
              url: 'calendar/challenges/?start=' + start.format() + '&end=' + end.format(),
              dataType: 'json',
              success: function(data) {
                  callback(JSON.parse(data));
              }
          });
      }

    })
});    