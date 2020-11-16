var colorRanges = {}
var socket

$(document).ready(function () {
	let selectedValue = null;
	socket = io()

	socket.on('connect', function() {
		socket.emit('message', {data: 'I\'m connected!'});

		socket.on('colores', function(rangos) {
			colorRanges = JSON.parse(rangos)
		})
	});

	$('#video').hide()

	$('#streaming-switch').change(function () {
		const stream = $(this).prop('checked')
		if (stream === true) {
			$.getJSON('/start');
			$('#video-frame').queue(function(next) {
				$(this).attr('src', '/video')
				$('#video').show()
				next()
			})
		}
		else {
			$.getJSON('/stop');
			$('#video-frame').queue(function(next) {
				$(this).attr('src', '')
				$('#video').hide()
				next()
			})
		}
	});

	$('#direction-switch').change(function () {
		$.getJSON('/direccion');
	});

	$('input[name=modo]').click(function () {
		const modo = $(this).val()

		_cambioModo(modo)

		$.ajax({
			url: '/modo/' + modo,
			data: JSON.stringify(_getOptions()),
			type: 'POST',
			dataType: 'json',
			contentType: "application/json; charset=utf-8",
			success: function (wsQuery) {
				console.log(wsQuery)
			}
		})
	});

	$('#velocidad-cinta').on('slide', function (slideEvt) {
		if (slideEvt.value !== selectedValue) {
			$.getJSON('/velocidad/' + slideEvt.value);
			selectedValue = slideEvt.value;
		}
	});

	$('#velocidad-cinta').slider({
		formatter: function (value) {
			return 'Current value: ' + value;
		}
	});

	$('#chk-show-id').change(function () {
		$.getJSON('/params/showID')
	});

	$('#chk-show-centroid').change(function () {
		$.getJSON('/params/showCentroid')
	});

	$('#chk-draw-contours').change(function () {
		$.getJSON('/params/drawContours')
	});

	$('#chk-show-forma').change(function () {
		$.getJSON('/params/showForma')
	});

	$('#chk-show-bounding-rect').change(function () {
		$.getJSON('/params/showBoundingRect')
	});

	$('#chk-show-measure').change(function () {
		$.getJSON('/params/showMeasure')
	});

	$('#chk-show-mask').click(function () {
		$.getJSON('/params/showMask')
	});

	const _getOptions = () => {
		return {
			showID: $('#chk-show-id').prop('checked'),
			showCentroid: $('#chk-show-centroid').prop('checked'),
			drawContours: $('#chk-draw-contours').prop('checked'),
			showForma: $('#chk-show-forma').prop('checked'),
			showBoundingRect: $('#chk-show-bounding-rect').prop('checked'),
			showMeasure: $('#chk-show-measure').prop('checked'),
			showMask: $('#chk-show-mask').prop('checked')
		}
	}

	const _cambioModo = (modo) => {
		const commonOptions = ['chk-show-id', 'chk-show-centroid',
													 'chk-draw-contours', 'chk-show-bounding-rect', 'chk-show-mask']
		const opcionesModos = {
			color: [...commonOptions, 'config-color'],
			forma: [...commonOptions, 'chk-show-forma', 'chk-show-measure'],
			codigo: [...commonOptions]
		}

 		$('#custom-options div').each(function(){
 			const chk = ($(this).children()[0]||{}).id || null

 			if (!chk)
 				return

			const found = opcionesModos[modo].find(m => m === chk);
			if (!found)
				$(this).hide(500);
			else
				$(this).show(500);
 		});
	}

	_cambioModo('color')

	// TODO: Tira error al presionar 2 veces el botón.
	$('#config-color').click(function (event) {
		var target = $('#config');
		target.load('/config-colores', function() {
			target.slideDown('fast')
		});

		event.preventDefault();
	});

});