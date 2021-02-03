var colorRanges = {}
var socket

$(document).ready(function () {
	let selectedValue = null;
	socket = io()

	socket.on('connect', function() {
		socket.emit('getColores', {});

		socket.on('colores', function(rangos) {
			colorRanges = JSON.parse(rangos)
		})

		socket.on('addList', function(data) {
			$('#tblObjetosDetectados > tbody:last-child').append(_genTableRow(JSON.parse(data)));
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
		const configColorButton = $('#config-color');

		_cambioModo(modo)

		if (modo === 'color')
			configColorButton.show();
		else
			configColorButton.hide();

		$.ajax({
			url: '/modo/' + modo,
			data: JSON.stringify(_getOptions()),
			type: 'POST',
			dataType: 'json',
			contentType: 'application/json; charset=utf-8',
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

	$('#chk-show-txt').change(function () {
		$.getJSON('/params/showTxt')
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
			showTxt: $('#chk-show-txt').prop('checked'),
			showBoundingRect: $('#chk-show-bounding-rect').prop('checked'),
			showMeasure: $('#chk-show-measure').prop('checked'),
			showMask: $('#chk-show-mask').prop('checked')
		}
	}

	const _cambioModo = (modo) => {
		const commonOptions = ['chk-show-id', 'chk-show-centroid', 'chk-show-txt',
													 'chk-draw-contours', 'chk-show-bounding-rect', 'chk-show-mask']
		const opcionesModos = {
			color: [...commonOptions, 'config-color'],
			forma: [...commonOptions, 'chk-show-measure'],
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
		$(this).hide();
		const divConfig = $('#config');

		divConfig.load('/config-colores', function() {
			divConfig.slideDown('fast')
		});

		event.preventDefault();
	});

	$('#configModal').on('show.bs.modal', function (event) {
	  const modo = $('input[name=modo]:checked').val();
	  const modal = $(this);
	  modal.find('.modal-title').text('Configurar ' + modo);
	})

// $('#imageModal').on('show.bs.modal', function(event) {
// 	console.log('hola')
// 	const image = $(this);
// 	console.log(image)
// })

	$(document).on('click', '.btn-image-modal', function() {
		var image = $(this).data('img');
		$('#imagen').attr('src', 'data:image/png;base64, ' + image);
	})

	// $('#boton-image-modal').on('click', function () {
	// 	console.log('entra')
 //    const image = $(this).data('img');
 //    console.log(image)
 //    $('#imagen').attr('src', image);
	// });

	const _genTableRow = (data) => {
		fecha = new Date()
		hora = fecha.getHours() + ':' + fecha.getMinutes() + ':' + fecha.getSeconds();
		return `<tr>
				      <th scope="row">${data.id}</th>
				      <td>${data.objeto}</td>
				      <td>${hora}</td>
				      <td align="center">
				      	<a href="#"
				      		 class="btn-image-modal"
				      		 data-img="${data.imagen}"
				      		 data-id="ISBN-001122"
				      		 data-toggle="modal"
				      		 data-target="#imageModal">
				      		<img width="64" height="48" src="data:image/png;base64, ${data.imagen}" />
				      	</a>
				      </td>
				    </tr>`;
	}

	const delTableRows = () => {
		$('#tblObjetosDetectados > tbody').empty();
	}
});