$(document).ready(function () {
	let selectedValue = null;

	var socket = io()

	socket.on('connect', function() {
		socket.emit('message', {data: 'I\'m connected!'});
	});

	// Se esconden opciones de video
	$('#video').hide()

  $("#video-frame")[0].onload = function() {
    console.log("done");
  }

	$('#streaming-switch').change(function () {
		if ($(this).prop('checked') === true) {
			$.getJSON('/start');
			$('#video-frame').fadeOut(500)
												.delay(600)
												.queue(function(next) {
													$('#video').show()
													$(this).attr('src', '/video')
													next()
												})
												.delay(600)
												.fadeIn(500);
		}
		else {
			$.getJSON('/stop');
			$('#video-frame').fadeOut(500)
												.delay(600)
												.queue(function(next) {
													$(this).attr('src', '')
													$('#video').hide()
													next()
												})
												.delay(600)
												.fadeIn(500);
		}
	});

	$("#direction-switch").change(function () {
		$.getJSON('/direccion');
	});

	$("input[name=modo]").click(function () {
		const modo = $(this).val()

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
});

