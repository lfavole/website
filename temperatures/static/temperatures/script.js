$(function() {
	var form = document.save_temp;

	$(document).on("keydown", function($event) {
		var event = $event.originalEvent;
		if(event.altKey && !event.ctrlKey && !event.shiftKey) {
			var key = event.key.toUpperCase();
			if(!isNaN(+key)) {
				var field = form.weather[+key - 1];
				if(field)
					field.checked = true;
				return false;
			}
			if(key == "D") {
				form.date.focus();
				return false;
			}
			if(key == "T") {
				form.temperature.focus();
				return false;
			}
			if(key == "N") {
				form.notes.focus();
				return false;
			}
			if(key == "V" || key == "0") {
				form.wind.checked = !form.wind.checked;
				return false;
			}
			if(document.activeElement == form.notes && key == "S") {
				document.getElementById("submit").click();
				return false;
			}
		}
	});

	function show_weekday() {
		var date = new Date(form.date.value);
		if(date === null) {
			$("#weekday").html("");
			return;
		}
		var fr_weekdays = [
			"dimanche",
			"lundi",
			"mardi",
			"mercredi",
			"jeudi",
			"vendredi",
			"samedi"
		];
		$("#weekday").html(fr_weekdays[date.getDay()]);
	}

	$(form).on("submit", function(event) {
		// remove the date warnings
		$(".date-warning").remove();

		// use an AJAX request to submit the form
		event.preventDefault();
		var formdata = new FormData(form);
		var ajax = new XMLHttpRequest();
		ajax.open("POST", location.href);
		ajax.onreadystatechange = function() {
			if(ajax.readyState == 4) {
				if(ajax.status == 200) {
					// show the missing / extra days
					$("#days").replaceWith(ajax.responseText);

					// next day
					var date = new Date(form.date.value);
					date.setDate(date.getDate() + 1);
					form.reset();

					// check if we need to add the next day
					var date_string = date.toISOString().split("T")[0];
					var date_matched = false;
					$("#days .missing a").each(function(_index, element) {
						if($(element).attr("href").substr(-10) == date_string) {
							date_matched = element;
							return false;
						}
					});
					if(date_matched) {
						form.date.value = date_string;
					} else {
						// set the date to the first missing day
						var first = $("#days .missing a").first();
						if(first.length) {
							var new_date = $(first).attr("href").substr(-10);
							form.date.value = new_date;
						}
						// remove the old warnings
						$(".date-warning").remove();
						// display a warning
						$('<span class="date-warning">').text("Attention : la date a changé !").insertAfter(form.date);
					}
					show_weekday();
					form.temperature.focus();
				} else {
					alert(
						"Erreur lors de l'enregistrement !\n\n"
						+ (/<title>[^<]*<\/title>/.exec(ajax.responseText) || "") + ""
					);
				}
			}
		};
		formdata.set("ajax", 1);
		ajax.send(formdata);
	});

	$('<span id="weekday">').insertBefore(form.date);
	$(form.date).on("change", show_weekday);
	show_weekday();

	$(".notes span").each(function(_index, element) {
		element.on("click", function() {
			// insert the note text
			var parts = this.innerHTML.split("...");
			insert($("#notes").get(0), parts[0], parts[1]);
		});
	});

	$("#days a").on("click", function(evt) {
        // set the date to the clicked day
        evt.preventDefault();
        var date = $(this).attr("href").substr(-10);
        form.date.value = date;
        show_weekday();
    });
});

function insert(element, start, end) {
	var scroll = element.scrollTop;
	if(document.selection) {
		element.focus();
		var sel = document.selection.createRange();
		sel.text = start + sel.text + end;
	} else if(element.selectionStart || element.selectionStart == "0") {
		var startPos = element.selectionStart;
		var endPos = element.selectionEnd;
		element.value = element.value.substring(0, startPos) + start + element.value.substring(startPos, endPos) + end + element.value.substring(endPos, element.value.length);
		element.selectionStart = startPos + start.length;
		element.selectionEnd = startPos + start.length + (endPos - startPos);
	} else {
		element.value += start + end;
	}
	element.scrollTop = scroll;
	element.focus();
}