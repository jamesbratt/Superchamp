$( document ).ready(function() {
	var challengeId = $('#myChart').attr('data-challenge-id');

	
	var marker;
	var elevationLocations = {};
	var $map = $('#route-detail-map');
	
	$.ajax({
		url: "/routes/coordinates/" + routeId,
		type: 'GET',
		success: function(data) {
			coords = JSON.parse(data);
		    map = L.map('route-detail-map').setView([50.736321, -3.536456], 13);

		    L.tileLayer('https://api.mapbox.com/styles/v1/mapbox/streets-v9/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFtZXNicmF0dCIsImEiOiJjaXlsN2kzangwMDFiMzJsamt2ODN2MndzIn0._5ybMQyFC60IomYbpwxBoQ', {
		        attribution: '© OpenStreetMap contributors'
		    }).addTo(map);
		    
		    var route = new L.Polyline(coords, {
		        color: '#EA1595',
		        weight: 6,
		        opacity: 1,
		        smoothFactor: 1
		    });
		    
		    route.addTo(map);
		    map.fitBounds(coords);
		},
		error: function (request, status, error) {
			console.log(error);
		}
	});
	
	if(challengeId !== undefined) {
		$('.select2').select2();
		
		$('.select2').on('select2:select', function (e) {
		    var data = e.params.data;
		    getData(data.id);
		});
		
		$('.select2').on('select2:unselect', function (e) {
		    var data = e.params.data;
		    config.data.datasets.splice(-1, 1);
            window.myChart.update();
		});

		function newDate(days) {
			return moment().add(days, 'd').toDate();
		}

		function newDateString(days) {
			return moment().add(days, 'd').format();
		}
		
		var config = {
		    type: 'line',
		    multiTooltipTemplate: "<%= labelString %> - <%= value %>",
		    data: {
				datasets: [],
		    },
		    options: {
		        scales: {
					xAxes: [{
						type: "linear",
						display: false,
						beginAtZero: false,
		            	ticks: {
		            		stepSize:1,
		            	},
		            	scaleShowLabels : false
					}],
					yAxes: [
						{
							display: true,
							id: 'speed',
							position: 'left',
			            	ticks: {
			            		beginAtZero: true,
			            	},
	                        scaleLabel: {
	                            display: true,
	                            labelString: 'Speed (km/h)'
	                        }
						}, {
							display: true,
							id: 'elevation',
							position: 'right',
			            	ticks: {
			            		beginAtZero: true,
			            	},
	                        scaleLabel: {
	                            display: true,
	                            labelString: 'Elevation (m)'
	                        }
							
						}
					]
		        },
		      	tooltips: {
		      		intersect: false,
		      		mode: 'index',
		      		callbacks: {
						title: function(tooltipItem, data) {return ''},
						label: function(tooltipItem, data) {
							if(tooltipItem.datasetIndex === 0) {
								return 'Elevation ' + tooltipItem.yLabel.toFixed(2) + ' m';
							} else {
								return tooltipItem.yLabel.toFixed(2) + ' km/h';
							}
							
						}
					}
		      	},
		        onClick: handleClick
		    }
		}
	
	    function formatSecsAsMins(time) {
	    	var formattedTime = moment.utc(time*1000).format('HH:mm:ss');
	    	return formattedTime;
	    }

		function handleClick(e) {
		    var item = window.myChart.getElementAtEvent(e)[0];
		    if (item) {
		        var label = window.myChart.data.datasets[item._datasetIndex];
		        var value = window.myChart.data.datasets[item._datasetIndex].data[item._index];
		    }
			   console.log(label);
			   console.log(value);		   
			};
		
		function renderStats() {      
			var ctx = document.getElementById("myChart").getContext('2d');
			Chart.defaults.LineWithLine = Chart.defaults.line;
			Chart.controllers.LineWithLine = Chart.controllers.line.extend({
			   draw: function(ease) {
			      Chart.controllers.line.prototype.draw.call(this, ease);

			      if (this.chart.tooltip._active && this.chart.tooltip._active.length) {
			         var activePoint = this.chart.tooltip._active[0],
			             ctx = this.chart.ctx,
			             x = activePoint.tooltipPosition().x,
			             topY = this.chart.scales['y-axis-0'].top,
			             bottomY = this.chart.scales['y-axis-0'].bottom;

			         // draw line
			         ctx.save();
			         ctx.beginPath();
			         ctx.moveTo(x, topY);
			         ctx.lineTo(x, bottomY);
			         ctx.lineWidth = 2;
			         ctx.strokeStyle = '#07C';
			         ctx.stroke();
			         ctx.restore();
			      }
			   }
			});	
			window.myChart = new Chart(ctx, config);
			getData(null);
		}
		
	    function getCookie(name) {
	        var cookieValue = null;
	        if (document.cookie && document.cookie != '') {
	            var cookies = document.cookie.split(';');
	            for (var i = 0; i < cookies.length; i++) {
	                var cookie = jQuery.trim(cookies[i]);
	                if (cookie.substring(0, name.length + 1) == (name + '=')) {
	                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
	                    break;
	                }
	            }
	        }
	        return cookieValue;
	    }
	
	    // Including CSRF token in ajax calls made to Django app
	    $.ajaxSetup({
	        beforeSend: function(xhr, settings) {
	            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
	                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
	            }
	        }
	    });

	    function getRandomColor() {
	    	  var letters = '0123456789ABCDEF';
	    	  var color = '#';
	    	  for (var i = 0; i < 6; i++) {
	    	    color += letters[Math.floor(Math.random() * 16)];
	    	  }
	    	  return color;
    	}
	    
	    function getData(challengeTimeId) {
	    	var url;

	    	if(challengeTimeId === null) {
	    		url = "/challenges/ajax-time-stats/" + challengeId;
	    	} else {
	    		url = "/challenges/ajax-time-stats/" + challengeId + "/?challengeTimeId=" + challengeTimeId;
	    	}

		    $.ajax({
		        url: url,
		        type: 'GET',
		        beforeSend: function(xhr, settings) {
		          $.ajaxSettings.beforeSend(xhr, settings);
		        },
		        success: function(data) {
		        	var label;
		        	var stats = JSON.parse(data.data);

		        	if(challengeTimeId === null) {
		        		label = 'Latest Effort';
		        		
			            var elevationDataset = {
			                label: 'elevation',
			                data: [],
			                fill: true,
			                yAxisID: 'elevation',
			                pointRadius: 0,
			                borderColor: 'rgba(255,255,255,0)',
			            };
			            
			            $.each(stats, function( index, data ) {
			            	var obj = {}
			            	obj['x'] = index + 1;
			            	obj['y'] = data.elevation;
			            	elevationDataset.data.push(obj);
			            })
			            
			            config.data.datasets.push(elevationDataset);
			       
		        	} else {
		        		label = data.label;
		        	}
		            var newDataset = {
		                label: label,
		                borderColor: getRandomColor(), 
		                data: [],
		                fill: false,
		                pointRadius: 0,
		                yAxisID: 'speed',
		            };
		            
		            $.each(stats, function( index, data ) {
		            	var obj = {}
		            	obj['x'] = index + 1;
		            	obj['y'] = data.speed;
		            	newDataset.data.push(obj);
		            })	       
		
		            config.data.datasets.push(newDataset);
		            window.myChart.update({duration:0});
		            
		        },
		        error: function (request, status, error) {
		        	console.log('error');
		        }
		      });
    	  }
	    
	      renderStats();
	}
   
});