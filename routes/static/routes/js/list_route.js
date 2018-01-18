$( document ).ready(function() {
	$('.box').each(function(i, box) {
		var id = $(box).attr('id')
		$.ajax({
			url: "/routes/coordinates/" + id,
			type: 'GET',
			success: function(data) {
				coords = JSON.parse(data);
			    mapId = $(box).find( ".route-map" ).attr('id');
			    map = L.map(mapId, { zoomControl:false,scrollWheelZoom:false }).setView([50.736321, -3.536456], 13);
			    map.dragging.disable();

			    L.tileLayer('https://api.mapbox.com/styles/v1/jamesbratt/cjaei11xx66rg2spoci7054wr/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFtZXNicmF0dCIsImEiOiJjaXlsN2kzangwMDFiMzJsamt2ODN2MndzIn0._5ybMQyFC60IomYbpwxBoQ', {
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
	});
})