function mot_pluriel(e, n) {
	if(n < 2 || e.match(/s(\s|$)/)) return e;
	return /\s/.test(e) ? e.replace(/([a-z]+)(\s+.*)/, "$1s$2") : e + "s";
}
function unite_pluriel(u, c) {
	return (/^(j|h|min|s|[A-Z]+|([mcdhkKMGgTt]|da)?[mLgo][²³]?)$/.test(u) ? u : mot_pluriel(u, c));
}

function countdown(options) {
    var color = options.color;
    var short_display = options.short_display;
    var one_digit = options.one_digit;
    var date = moment(options.date).toDate().getTime();
    var container = $(options.element).addClass("countdown");
    var texts = options.texts || options.txts || {
		0: "CPT",
		[-Infinity]: "Le compte à rebours est fini !"
	};
	if(texts["-inf"] || texts.inf) {
		texts[-Infinity] = texts["-inf"] || texts.inf;
		delete texts["-inf"];
		delete texts.inf;
	}
    var texts_keys = Object.keys(texts).sort().reverse();

	if(options.anim != false)
		container.addClass("anim");

    var max_duration = moment.duration(10, "y").add(-1, "ms")._data;
    var units = [
        ["y", "an"],
        ["M", "mois"],
        ["d", "j"],
        ["h", "h"],
        ["m", "min"],
        ["s", "s"],
    ];
    var short_units = ["h", "m", "s"];
    var required_units = ["h", "m", "s"];

    var previous_text;
    var timeout;
	var callback = function() {
		var start = performance.now();
		var now = new Date().getTime();
		var distance = date - now;

		var diff = moment.duration(Math.abs(distance));
        var ms = diff.get("ms");
        if(Math.abs(ms) < 500)
            diff.add(-ms, "ms");  // round down
        else
            diff.add(ms, "ms");  // round up
		var dst1 = moment(date).isDST();
		var dst2 = moment(now).isDST();
		if(dst1 != dst2)
			diff.add(dst1 && !dst2 ? 1 : -1, "hours");
		var html = [];
		for(var display_next = false, diff_value, unit, i = 0, l = units.length; i < l; i++) {
			unit = units[i][0];
			diff_value = diff.get(unit);
			display_next = display_next || diff_value;
			html.push([
				diff_value,
				unite_pluriel(units[i][1], diff_value),
				unit,
                // always show seconds
				unit == "s" || (required_units.includes(unit) ? display_next : diff_value)
			]);
			if(i != l - 1)
                // add a spacer for all elements except for the last element
                html.push(
                    '<span class="spacer">'
                    + (short_display && short_units.includes(unit) ? ":" : " ")
                    + "</span>"
                );
		}

		html = html.map(function(part) {
			if(typeof part == "string") return part;
            var diff_value = part[0];
            var diff_value_str = diff_value + "";
            var verbose_unit = part[1];
            var unit = part[2];
            var display = part[3];

            // add zero at start
			if(!one_digit && short_units.includes(unit) && diff_value < 10)
                diff_value_str = "0" + diff_value_str;
			var css_colors = [];
			var classes = [];
			if(!display)
				classes.push("hidden");
			else if(color)
				css_colors.push(
                    "color:"
                    + (typeof color == "function" ? color(diff_value, unit, max_duration[moment.normalizeUnits(unit) + "s"] + 1) : color)
                );
			return (
                "<span"
                + (classes.length ? ' class="' + classes.join(" ") + '"' : "")
                + (css_colors.length ? ' style="' + css_colors.join("; ") + '"' : "")
                + ">"
                + (diff_value_str.replace(/(.)/g, '<span data-digit="$1">$1</span>') || "<span></span>")
                + (short_display && short_units.includes(unit) ? "" : " <small>" + verbose_unit + "</small>")
                + "</span>"
            );
		});
		for(var key, i = 0, l = texts_keys.length; i < l; i++) {
            key = texts_keys[i];
			if(distance > key * 1000) {
				var text = typeof texts[key] == "function" ? texts[key]() : texts[key];
				if(previous_text != text) {
					container.html(text.replace(/CPT/g, html.join("")));
                    previous_text = text;
                } else {
                    $.each(html, function(index, new_element) {
                        new_element = $(new_element);
                        if(new_element.text() == new_element.html()) {  // text elements
                            var element = container.eq(index);
                            new_element.toggleClass("hidden", element.hasClass("hidden"));  // copy hidden class
                            if(new_element.attr("style") != element.attr("style"))
                                new_element.attr("style", element.attr("style"));  // copy style
                            if(new_element.html() != element.html())
                                new_element.html(element.html());  // copy content
                            return;
                        }
                        // if(new_element.find("> span").length == 1)
                        //     new_element.prepend($("<span>").hide());  // add a second span if not present
                        var element = container.find("> span").eq(index);
                        element.toggleClass("hidden", new_element.hasClass("hidden"));
                        if(element.attr("style") != new_element.attr("style"));
                        element.attr("style", new_element.attr("style"));
                        for(var t, t2, nb = 0, l = new_element.children().length; nb < l; nb++) {
                            t = element.children().eq(nb);
                            t2 = new_element.children().eq(nb);
                            t.toggleClass("hidden", t2.hasClass("hidden"));  // copy hidden class
                            if(t.attr("style") != t2.attr("style"))
                                t.attr("style", t2.attr("style"));  // copy style
                            var d1 = t.attr("data-digit");
                            var d2 = t2.attr("data-digit");
                            if(d1 != d2) {
                                // add transition
                                t.html('<span class="prev">' + d1 + '</span><span class="act">' + d2 + '</span>')
                                t.attr("data-digit", d2);
                            }
                        }
                    });
                }
				break;
			}
		}
		var end = performance.now();
		timeout = setTimeout(
            callback,
            (
                // 700 ms  => wait 700 ms
                // -700 ms => wait 300 ms
                ms < 0 ? 1000 - -ms : ms
            ) - (end - start),
        );
	};
	callback();
}