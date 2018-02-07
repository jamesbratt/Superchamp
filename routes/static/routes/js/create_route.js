google.charts.load('current', {packages: ['corechart']});

$( document ).ready(function() {

	var $header = $('.main-header').outerHeight();
	var $contentHeader = $('.content-header').outerHeight();
	var $footer = $('#footer').outerHeight();
	var $controls = $('#builder-controls').outerHeight();
	var $map = $('#route-builder-map');

    var $window = $(window).on('resize', function(){
        var height = $(this).height() - $header - $contentHeader - $footer - $controls - 45;
        $map.height(height);
    }).trigger('resize');

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

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
            }
        }
    });

    var StageCoordinates  = Backbone.Model.extend({
        defaults: {
            coordinates: null,
            distance: null,
            start_lat: null,
            start_long: null,
            finish_lat: null,
            finish_long: null,
            min_elevation: null,
            max_elevation: null,
            elevation_gain: null,
        }
    });

    var StageRouteView = Backbone.View.extend({
        el: '#builder-content',
        map: L.map('route-builder-map').setView([50.736321, -3.536456], 10),
        control: null,
        elevationChart: null,
        elevationRawData: null,
        marker: null,
        elevationLocations: {},

        events: {
            'click #clear-route': 'clearRoute',
            'click #save-stage': 'showPopUp',
            'click #create-stage': 'saveStage',
            'click #undo-waypoint': 'undoWaypoint',
        },

        initialize: function() {
            _.bindAll(this, 'render', 'constructRoute', 'drawChart', 'getElevationData', 'addChartData', 'showLineCircle');
            this.render();
            this.createRoutingControl();
        },

        clearRoute: function() {
            this.control.getPlan().setWaypoints([]);
            this.elevationChart.clearChart();
            this.hideLineCircle();

            $('#distance-wrapper').empty();
            $('#gain-wrapper').empty();
            $('#minEle-wrapper').empty();
            $('#maxEle-wrapper').empty();
            this.map.on('click', this.constructRoute);
        },

        undoWaypoint: function() {
            this.control.spliceWaypoints(this.control.getWaypoints().length - 1, 1);
            this.hideLineCircle();
        },

        saveStage: function(e) {
            e.preventDefault();
            var that = this;

            var polyline = L.polyline(stageModel.get('coordinates'));

            var stagePayload = {
                'title':$('#id_title').val(),
                'difficulty':$('#id_difficulty').val(),
                'country':$('#id_country').val(),
                'locality':$('#id_locality').val(),
                'polyline': polyline.encodePath(),
                'distance': stageModel.get('distance'),
                'start_lat': stageModel.get('start_lat'),
                'start_long': stageModel.get('start_long'),
                'finish_lat': stageModel.get('finish_lat'),
                'finish_long': stageModel.get('finish_long'),
                'min_elevation': stageModel.get('min_elevation'),
                'max_elevation': stageModel.get('max_elevation'),
                'elevation_gain': stageModel.get('elevation_gain'),
            };

            $.ajax({
                url: "/routes/ajax-create/",
                type: 'POST',
                data: stagePayload,
                beforeSend: function(xhr, settings) {
                    $.ajaxSettings.beforeSend(xhr, settings);
                },
                success: function(data) {
                    $('#saveRouteModal').modal('hide');
                    that.elevationChart.clearChart();
                    that.hideLineCircle();
                    that.control.getPlan().setWaypoints([]);

                    $('#distance-wrapper').empty();
                    $('#gain-wrapper').empty();
                    $('#minEle-wrapper').empty();
                    $('#maxEle-wrapper').empty();

                    window.location.replace('success/' + data);
                },
                error: function (request, status, error) {
                    $('#stage-create-form-wrapper .alert-danger').remove();
                    if(request.responseJSON.title) {
                        msg = 'Give the stage a title!';
                    } else {
                        msg = 'Your route was invalid, please start again.'
                    }
                    $('#stage-create-form-wrapper').prepend('<div class="alert alert-danger" role="alert">'+ msg +'</div>')
                }
            });

        },

        constructRoute: function(e) {
            var that = this;
            var container = L.DomUtil.create('div'),
            startBtn = that.createButton('Start route from here', container, 'success'),
            destBtn = that.createButton('Finish route here', container, 'info');

            L.DomEvent.on(startBtn, 'click', function() {
                that.control.spliceWaypoints(0, 1, e.latlng);
                that.map.closePopup();
            });

            L.DomEvent.on(destBtn, 'click', function() {
                that.control.spliceWaypoints(that.control.getWaypoints().length - 1, 1, e.latlng);
                that.map.closePopup();
                that.map.off('click', that.constructRoute);
            });

            L.popup()
            .setContent(container)
            .setLatLng(e.latlng)
            .openOn(that.map);
        },

        showPopUp: function() {
            $('#saveRouteModal').modal('show');
        },

        hideLineCircle: function() {
            if(this.marker != undefined) {
                this.map.removeLayer(this.marker);
                this.marker = undefined;
            }
        },

        showLineCircle: function(e) {
            this.elevationChart.setSelection(e.row, e.column);
            var value = data.getValue(e.row, e.column);

            if(this.marker == undefined) {
                this.marker = L.circleMarker([this.elevationLocations[value].lat,this.elevationLocations[value].long],200, {color:'#EA57BE', fillColor:'#EA57BE', opacity:1}).addTo(this.map);
            } else {
                this.marker.setLatLng([this.elevationLocations[value].lat,this.elevationLocations[value].long]);
            }
            this.marker.bringToFront();
        },

        calculateElevationGain: function(data) {
            var gain = 0;
            var totalGain = 0;

            $.each(data, function( index, elevation ) {
                ele = parseFloat(elevation.elevation.toFixed(2))
                if(ele > gain) {
                    diff = ele - gain;
                    totalGain = totalGain + diff;
                }
                gain = ele;
            })

            return totalGain.toFixed(2);
        },

        getElevationMetrics: function() {
            var sortedElevationData = [];
            var minElevation;
            var maxElevation;
            var elevationGain;

            function sortNumber(a,b) {
                return a - b;
            }

            $.each(this.elevationRawData, function( index, elevation ) {
                sortedElevationData.push(parseFloat(elevation.elevation.toFixed(2)))
            })

            sortedElevationData.sort(sortNumber);
            minElevation = sortedElevationData[0]
            maxElevation = sortedElevationData.slice(-1).pop();
            elevationGain = this.calculateElevationGain(this.elevationRawData);

            return {'min':minElevation, 'max':maxElevation, 'gain':elevationGain};
        },

        drawChart: function() {
            this.elevationChart = new google.visualization.LineChart(document.getElementById('elevation_chart'));
            google.visualization.events.addListener(this.elevationChart, 'onmouseover', this.showLineCircle);
        },

        getElevationData: function(path) {
            var that = this;
            var elevator = new google.maps.ElevationService;
            elevator.getElevationAlongPath({
                'path': path,
                'samples': 500
            }, that.addChartData);
        },

        createButton: function(label, container, btnClass) {
            var btn = L.DomUtil.create('button', '', container);
            btn.setAttribute('type', 'button');
            btn.setAttribute('class', 'btn btn-' + btnClass);
            btn.setAttribute('style', 'margin:0.1em');
            btn.innerHTML = label;
            return btn;
        },

        addChartData: function(elevations, status) {
            this.elevationRawData = elevations;
            data = new google.visualization.DataTable();
            data.addColumn('string', 'Sample');
            data.addColumn('number', 'Elevation');

            for (var i = 0; i < elevations.length; i++) {
                data.addRow(['', elevations[i].elevation]);
                this.elevationLocations[elevations[i].elevation] = {'lat':elevations[i].location.lat(),'long':elevations[i].location.lng()};
            }
            this.elevationChart.draw(data, {
                height: 150,
                legend: 'none',
                titleY: 'Elevation (m)',
                colors: ['red'],
            });

            var eleMetrics = this.getElevationMetrics();
            stageModel.set('min_elevation', eleMetrics.min);
            stageModel.set('max_elevation', eleMetrics.max);
            stageModel.set('elevation_gain', eleMetrics.gain);

            $('#gain-wrapper').empty();
            $('#gain-wrapper').append(stageModel.get('elevation_gain') + ' m');

            $('#minEle-wrapper').empty();
            $('#minEle-wrapper').append(stageModel.get('min_elevation') + ' m');

            $('#maxEle-wrapper').empty();
            $('#maxEle-wrapper').append(stageModel.get('max_elevation') + ' m');

        },

        createRoutingControl: function() {

            var that = this;

            this.control = L.Routing.control({
                router: L.Routing.mapbox('pk.eyJ1IjoiamFtZXNicmF0dCIsImEiOiJjaXlsN2kzangwMDFiMzJsamt2ODN2MndzIn0._5ybMQyFC60IomYbpwxBoQ'),
                waypoints: [],
                show: false,
                waypointMode: 'snap',
                lineOptions: {
                    styles: [
                        {color: '#EA1595', opacity: 0.8, weight: 5},
                    ]
                },
                routeWhileDragging: true
            }).addTo(this.map).on('routeselected', function (e) {
                that.hideLineCircle();
                that.getElevationData(e.route.coordinates);

                stageModel.set('coordinates', e.route.coordinates);
                stageModel.set('distance', that.control._selectedRoute.summary.totalDistance);
                stageModel.set('start_lat', that.control.getWaypoints().slice(0)[0].latLng.lat);
                stageModel.set('start_long', that.control.getWaypoints().slice(0)[0].latLng.lng);
                stageModel.set('finish_lat', that.control.getWaypoints().slice(-1)[0].latLng.lat);
                stageModel.set('finish_long', that.control.getWaypoints().slice(-1)[0].latLng.lng);

                var distancekm = that.control._selectedRoute.summary.totalDistance/1000;
                $('#distance-wrapper').empty();
                $('#distance-wrapper').append(distancekm.toFixed(2) + ' Km');
            });

            this.map.on('click', this.constructRoute);
        },

        render: function() {
            $('#instructionsModal').modal('show');
            L.tileLayer('https://api.mapbox.com/styles/v1/jamesbratt/cjaei11xx66rg2spoci7054wr/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoiamFtZXNicmF0dCIsImEiOiJjaXlsN2kzangwMDFiMzJsamt2ODN2MndzIn0._5ybMQyFC60IomYbpwxBoQ', {
                attribution: '© OpenStreetMap contributors'
            }).addTo(this.map);

            google.charts.setOnLoadCallback(this.drawChart);

            return this;
        },
    });
    new StageRouteView();
    var stageModel = new StageCoordinates();
});