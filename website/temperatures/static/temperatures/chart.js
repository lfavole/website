/* global Highcharts, data, weather */
$(function() {
	var real_data = {
		temperature: [],
		max_temp: [],
		snow_cm: []
	};
	function add(list, element) {
		list[list.length] = element;
	}
	function get_null(element) {
		// undefined => null
		return typeof element == "undefined" ? null : element;
	}
	var date, old_date, days_to_add;
	for(var el, i = 0, l = data.length; i < l; i++) {
		el = data[i];
		date = Date.UTC(el[0], el[1], el[2]);
		if(old_date && date - old_date != 86400000) {
			days_to_add = (date - old_date) / 86400000;
			for(var j = 0; j < days_to_add; j++)
				add(real_data.temperature, [old_date + j * 86400000, null]);
		}
		add(real_data.temperature, {
			x: date,
			y: el[3],
			marker: {
				symbol: "url(/static/temperatures/icons/" + el[4] + "_small.png)",
				width: 30,
				height: 30
			}
		});
		add(real_data.snow_cm, [date, get_null(el[5])]);

		if(typeof el[6] != "undefined")
			add(real_data.max_temp, [date, get_null(el[6])]);
			// placeholder to avoid linking points
		else
			add(real_data.max_temp, [date, null]);

		old_date = date;
	}

	Highcharts.setOptions({
		lang: {
			loading: "Chargement...",
			months: "janvier février mars avril mai juin juillet août septembre octobre novembre décembre".split(" "),
			shortMonths: "janv. févr. mars avr. mai juin juil. août sept. oct. nov. déc.".split(" "),
			weekdays: "dimanche lundi mardi mercredi jeudi vendredi samedi dimanche".split(" "),
			decimalPoint: ",",
			numericSymbols: "KMGTPE".split(""),
			resetZoom: "Réinitialiser le zoom",
			resetZoomTitle: "Réinitialiser le zoom à 1:1",
			thousandsSep: " ",
		},
        tooltip: {
            dateTimeLabelFormats: {
                day: "%e %b",
                week: "%e %b",
                month: "%B %Y",
                year: "%Y",
            },
        },
		credits: {enabled: false},
	});

	Highcharts.chart("temperatures-chart", {
		chart: {zoomType: "x"},
		title: {text: "Températures"},
		xAxis: {
			type: "datetime",
			minTickInterval: 24 * 36e5,
			dateTimeLabelFormats: {day: "%e %b"}
		},
		yAxis: [{
			// Primary yAxis
			labels: {format: "{value}°C"},
			title: {text: "Température"},
			plotLines: [{
				value: 2,
				color: "blue",
				dashStyle: "Dash",
				width: 1,
				label: {
					text: "Gel",
					style: {
						fontWeight: "bold",
						fontSize: 16,
						color: "blue"
					}
				}
			}, {
				value: 20,
				color: "red",
				dashStyle: "Dash",
				width: 1,
				label: {
					text: "Canicule",
					style: {
						fontWeight: "bold",
						fontSize: 16,
						color: "red"
					}
				}
			}]
		}, {
			// Secondary yAxis
			gridLineWidth: 0,
			title: {text: "Cm de neige"},
			labels: {format: "{value} cm"},
			opposite: true
		}],
		tooltip: {shared: true},
		legend: {
			layout: "vertical",
			align: "right",
			verticalAlign: "middle"
		},
		plotOptions: {
			series: {
				label: {connectorAllowed: false},
				marker: {
					symbol: "circle",
					radius: 10
				}
			}
		},
		series: [{
			name: "Température minimale",
			type: "spline",
			data: real_data.temperature,
			tooltip: {
				xDateFormat: "%e %B %Y",
				valueSuffix: "°C"
			},
			states: {hover: {halo: {size: 20}}}
		}, {
			name: "Température maximale",
			type: "line",
			data: real_data.max_temp,
			tooltip: {
				xDateFormat: "%e %B %Y",
				valueSuffix: "°C"
			}
		}, {
			name: "Cm de neige",
			type: "column",
			yAxis: 1,
			data: real_data.snow_cm,
			tooltip: {
				xDateFormat: "%e %B %Y",
				valueSuffix: " cm"
			},
			// pointWidth: 20,
			grouping: false,
			dataLabels: {
				enabled: true,
				filter: {
					operator: ">",
					property: "y",
					value: 0
				},
				format: "{y} cm"
			}
		}],
		responsive: {
			rules: [{
				condition: {maxWidth: 500},
				chartOptions: {
					legend: {
						layout: "horizontal",
						align: "center",
						verticalAlign: "bottom"
					}
				}
			}]
		}
	});

	Highcharts.chart("weather-pie-chart", {
		chart: {type: "pie"},
		title: {text: "Temps"},
		plotOptions: {
			pie: {
				allowPointSelect: true,
				cursor: "pointer",
				dataLabels: {
					enabled: true,
					format: "<b>{point.name}</b>: {point.percentage:.1f} %"
				}
			}
		},
		series: [{
			name: "Temps",
			data: weather,
			tooltip: {
				xDateFormat: "%e %B %Y",
				valueSuffix: " jours"
			}
		}]
	});
});