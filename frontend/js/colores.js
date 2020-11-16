const r = ['h', 's', 'v']
let inHTML = ''
let sliders = []
const _genHTMLSlider = (h, val, idSlider) => {
	return `<div "class="row">
						<label for="`+val+idSlider+`">`+val+`</label>
						<input id="`+val+idSlider+`"
									 data-slider-id="s-`+val+idSlider+`"
									 type="text"
									 data-slider-min="0"
									 data-slider-max="255"
									 data-slider-step="1"
									 data-slider-value="`+h+`"/>
				 	</div>`
}

$.each(colorRanges, function(color, ranges) {
	inHTML += `<div id="`+color+`" class="row row-cols-2">`
	$.each(colorRanges[color], function(index, v) {
		inHTML += `<div class="col">
							   <div class="row justify-content-center">`+
							   	 color.toUpperCase() +` `+
							   	 index.toUpperCase() +`
							   </div>
							   <div class="row">`
		$.each(colorRanges[color][index], function(idx, value) {
			inHTML += `<div class="col align-self-center border">`
			for (let i = 0; i <= 2; i++) {
				const strR = r[i]+'-'
				const idSlider = color + '-' + index + '-' + idx
				sliders.push(strR+idSlider)
				inHTML += _genHTMLSlider(colorRanges[color][index][idx][i],
																 strR,
																 idSlider)
			}
			inHTML += `</div>`
		})
		inHTML += `</div></div>`
	})
	inHTML += `</div>`
})

$("#rangos").html(inHTML);

$(document).ready(function () {

	$('#red').hide()
	$('#blue').hide()
	$('#yellow').hide()

	$('#btnRed').click(function() {
		$('#red').toggle();
	});

	$('#btnBlue').click(function() {
		$('#blue').toggle();
	});

	$('#btnYellow').click(function() {
		$('#yellow').toggle();
	});

	$.each(sliders, function(k, slider) {
		$('#'+slider).slider({
			formatter: function (value, id) {
	      const keys = $(this)[0].id.split('-')
	      const keyValue = r.findIndex(v => {return v === keys[1]})
	      colorRanges[keys[2]][keys[3]][keys[4]][keyValue] = value
				socket.emit('setColores', {data: colorRanges})
				return value
			}
		});
	});

});