var banner = (function() {
	var $ = window.jQuery;
	if(!$) return false;
	var container = null;
	function add(e) {
		if(!container) return;
		if($.type(e) == "string")
			e = $("<div>").text(e)
		container.append(e);
		function close() {
			$(e).addClass("closing");
			setTimeout(function() {
				$(e).remove();
			}, 400);
		}
		e.banner = {
			close: close
		};
		return e.banner;
	}
	function close(e) {
		$(e || (container ? container.children() : "")).each(function(i, e) {
			if(e.banner)
				e.banner.close();
		});
	}
	$.fn.banner = function() {
		return add(this), this;
	};
	$.fn.bannerClose = function() {
		return close(this), this;
	};
	$(function() {
		container = $('<div class="banners">').appendTo("body");
	});
	return {
		add: add,
		close: close
	};
})();
var audioplayer = (function() {
	var $ = window.jQuery;
	if(!$) return false;
	var audios = {};
	var audios_global = {};
	var audios_number = 0;
	var last_played = 0;
	var autoplay_has_been_set = 0;

	var down = 0;
	var down_icon = 0;
	var has_moved = 0;
	var add_banner = true;
	var updating_progress = false;

	var floor = Math.floor;

	function get_x_from_event(event) {
		// return (event.changedTouches ? event.changedTouches[0] : event).pageX;
		return (event.changedTouches || [event])[0].pageX;
	}
	function limit(number, min, max) {
		return Math.min(Math.max(min, number), max);
	}
	function format_time(time) {
		if(isNaN(time))
			return "--:--:--";
		if(time >= 3600)
			return floor(time / 3600) + ":" + ("00" + floor((time % 3600) / 60)).substr(-2) + ":" + ("00" + floor(time % 60)).substr(-2);
		else
			return floor(time / 60) + ":" + ("00" + floor(time % 60)).substr(-2);
	}
	function init(elements, opt, opt_r) {
		$(elements || "audio").each(function(_index, element) {
			if(element.audioplayer) return;
			var is_banner = add_banner && element == $banner_audio[0];
            if(!is_banner)
                $banner_audio.parent().show();
			var $element = $(element);
			function get_element() {
				if(is_banner)
					return audios_global[last_played];
				return element;
			}
			var t_updating_progress;
			start();
			var o = $.extend(opt, {
				scratch: typeof $element.attr("data-scratch") != "undefined",
				autoplay: element.autoplay,
				lyrics: $element.attr("data-lyrics"),
				offset: $element.attr("data-offset")
			}, opt_r);
			if(autoplay_has_been_set)
				// only one audio element can have autoplay
				o.autoplay = false;
			if(element.autoplay)
				autoplay_has_been_set = 1;
			function set_icon_class(c) {
				$icon.attr("class", "icon " + c);
			}
			function get_time_from_event(evt) {
				var l = $bar.offset().left, w = $bar.innerWidth() || 1;
				return limit(get_x_from_event(evt) - l, 0, w) / w * get_element().duration;
				// return (limit(getX(evt), l, l + w) - icon.innerWidth() / 2) / w * e.duration;
			}
			function set_current_time(evt, set = true) {
				var time = evt.type == "loadedmetadata" ? 0 : get_time_from_event(evt);
				if(set && !is_banner) {
					clearTimeout(t_updating_progress);
					updating_progress = true;
					get_element().currentTime = time;
					t_updating_progress = setTimeout(function() {updating_progress = false}, 50);
				}
				update_prog(time);
			}
			function update_buffered() {
				var el = get_element();
				var length = el.buffered.length ? el.buffered.end(0) : 0;
				var percentage = length / (el.duration || 1) * 100;
				$buffered.css("width", percentage + "%");
				if(percentage >= 100) clearInterval(i_buffered);
			}
			function update_prog(time) {
				var current_time = time || get_element().currentTime, duration = get_element().duration || 1;
				$icon.css("left", limit(current_time / duration * 100, 0, 100) + "%");
				$time.text(format_time(current_time) + " / " + format_time(duration));
			}
			function play_pause(el) {
				if(el.paused || el.ended)
					el.play().catch(function() {
						el.pause();
						$(el).trigger("playerror");  // set the icon state on the banner audio too
					});
				else
					el.pause();
			}
			function display_metadata() {
				if(!is_banner) return;
				var url = get_element().src;
				$(".currently-playing").text(url);
				if(!window.jsmediatags || url.slice(0, 5) == "file:")
					return;
				jsmediatags.read(url, {
					"onSuccess": function(tag) {
						window.tags = tag.tags;
						var tags = tag.tags;
						var $currently_playing = $(".currently-playing").empty();
						if(tags.picture) {
							var picture_url = URL.createObjectURL(new Blob(
								[new Uint8Array(tags.picture.data)],
								{"type": tags.picture.format},
							));
							$currently_playing.append($('<img class="song-picture">').attr("src", picture_url));
						}
						$currently_playing
						.append($('<div class="song-title">').text(tags.title))
						.append($('<div class="song-artist">').text(tags.artist))
						.append($('<div class="song-album">').text(tags.album));
					}
				});
			}
			var n = ++audios_number;
			if(!last_played && !is_banner) last_played = n;
			element.audioplayer = n;
			audios[n] = [n, move, up];
			audios_global[n] = element;

			var t_wait, i_buffered;

			var $icon = $('<div class="icon off" draggable="false">')
			.on("mousedown touchstart", function() {
				down_icon = 1;
				// falls back to the bar
			});
			var $buffered = $('<div class="buffered">');
			var $bar = $('<div class="bar">').append($buffered).append($icon)
			.on("mousedown touchstart", function() {
				down = n;
				has_moved = 0;
			});
			var $time = $('<div class="time">').on("dblclick", function(evt) {
				var time = prompt("Time:");
				if(!time) return;
				var e = get_element();
				if(+time < 1){
					e.currentTime = +time * e.duration;
					return;
				}
				var match = /^(?:(\d+):)??(?:(\d+):)?(\d+(?:\.?\d+)?)$/.exec(time);
				time = +(match[1] || 0) * 3600 + +(match[2] || 0) * 60 + +(match[3] || 0);
				e.currentTime = time;
			});
			$('<div class="audioplayer">').insertBefore(element)
			.append($bar)
			.append($time)
			.append(
				$element.detach().hide()
				.on("waiting", function(evt) {
					if(evt.target != $banner_audio[0])
						t_wait = setTimeout(function() {
							set_icon_class("load");
						}, 50);
				})
				.on("play playing", function() {
					clearTimeout(t_wait);
					set_icon_class("play");
					if(!is_banner && last_played != n)
						audios_global[last_played].pause();
					if(!is_banner)
						last_played = n;
					display_metadata();
				})
				.on("pause", function() {
					set_icon_class("off");
				})
				.on("playerror", function() {
					set_icon_class("error");
				})
				.on("timeupdate", function() {
					if(is_banner || down != n) update_prog();
				})
				.on("seeking seeked", function() {
					update_prog();
				})
				.on("ended", function(evt) {
					if(updating_progress) return;
					evt.target.currentTime = 0;
					var audiolist = $(evt.target).closest(".audiolist");
					if(!audiolist.length) return;
					var audios = audiolist.find("audio");
					var next = false;
					var audio = null;
					audios.each(function(_index, element_to_try) {
						if(next) {
							audio = element_to_try;
							return false;
						}
						if(element == element_to_try)
							next = true;
					});
					if(next && audio == null && audiolist.attr("data-repeat"))
						audio = audios[0]
					if(!audio) return;
					var $autoplay = $("<div>");
					var remaining_time = 5;
					var ret = null;
					function callback() {
						if(ret != null)
							return;
						if(!remaining_time) {
							audio.play();
							swal.close();
							return;
						}
						$autoplay.text("Lecture automatique dans " + remaining_time + " seconde" + (remaining_time >= 2 ? "s" : "") + "...");
						remaining_time--;
						setTimeout(callback, 1000);
					};
					swal($autoplay[0], {"buttons": ["Annuler", "OK"]})
					.then(function(value) {
						if(value) {
							audio.play();
							return;
						}
						ret = false;
					});
					callback();
				})
				.one("loadedmetadata", function(evt) {
					set_icon_class(evt.target.paused ? "off" : "play");
					set_current_time(evt, false);
					if(o.autoplay) play_pause(evt.target);
				})
				.one("progress", function() {
					i_buffered = setInterval(update_buffered, 500);
				})
			);
			if(add_banner && element != $banner_audio[0]) {
				// send all events to the banner audio
				function trigger(evt) {
					if(!is_banner && last_played == n || evt.type == "play") $banner_audio.trigger(evt);
				}
				$element
				.on("waiting play playing pause playerror timeupdate seeking seeked", trigger)
				.one("loadedmetadata progress", trigger);
			}
			function move(evt) {
				if(down_icon) $icon.addClass("drag");
				has_moved = 1;
				set_current_time(evt.originalEvent, o.scratch || element.paused);
			}
			function up(evt) {
				if(!has_moved && down_icon)
					play_pause(get_element());
				else
					set_current_time(evt.originalEvent);
				$icon.removeClass("drag");
			}
			if(!element.preload)
				element.preload = "metadata";
			if(o.lyrics)
				lyrics.init(element, {lyrics: o.lyrics, offset: o.offset});
		});
	}
	var started = 0;
	function start() {
		if(started) return;
		started = 1;
		$(window)
		.on("mousemove touchmove", function(e) {
			// move(e);
			if(down) audios[down][1](e);
		})
		.on("mouseup touchend", function(e) {
			// up(e);
			if(down) audios[down][2](e);
			down = 0; down_icon = 0; has_moved = 0;
		})
		.on("keydown", function(e) {
			if(e.keyCode == 27) { // Escape
				down = 0; down_icon = 0; has_moved = 0;
			}
		});
	}
	$.fn.audioplayer = function() {
		return init(this), this;
	};
	var $banner_audio;
	if(add_banner)
		$(function() {
			banner.add(
				$("<div>")
				.append($('<div class="currently-playing">'))
				.append($banner_audio = $("<audio>"))
                .hide()
			);
			init($banner_audio);
		});
	$(function() {
		init();
		var mo = new MutationObserver(function(change) {
			init(change.addedNodes);
			$(change.removedNodes).each(function(_index, element) {
				$(element).parent().remove();
			});
		});
		mo.observe(document.body, {"childList": "audio"});
	});
	return {
		init: init,
		getLast: function() {
			return last_played;
		},
		getAudios: function() {
			return audios_global;
		},
		getAudiosNumber: function() {
			return audios_number;
		}
	};
})();
var lyrics = (function() {
	function is_string(e) {
		return typeof e == "string";
	}
	function sort_stable(e, f) {
		return e.map(function(e, i) {
			return [i, e];
		}).sort(function(a, b) {
			return f(a[1], b[1]) || a[0] - b[0];
		}).map(function(e) {
			return e[1];
		});
	}
	var canvas, video;
	function init_canvas() {
		if(canvas) return;
		canvas = $("<canvas>").addClass("sr-only").appendTo("body")[0];
		canvas.width = 1024;
		canvas.height = 512;
		var ctx = canvas.getContext("2d");
		ctx.fillStyle = "white";
		ctx.fillRect(0, 0, canvas.width, canvas.height);

		video = $("<video>")[0];
		video.srcObject = canvas.captureStream();
		video.muted = true;
		video.play();
	}
	function init(e, opt, opt_r) {
		$(e || ".lyrics").each(function(_index, element) {
			if(element.lyrics) return;

			var $lyrics = $('<div class="paroles">');
			var $dropdown = $('<div class="dropdown">').append('<a href="#" class="icon">≡').appendTo($lyrics);
			var $dropdown_content = $('<div class="content">').appendTo($dropdown);
			$('<a href="#">').text("Canvas").css("font-size", "1rem").appendTo($dropdown_content).on("click", function(evt) {
				evt.preventDefault();
				if(!video || video != document.pictureInPictureElement) {
					init_canvas();
					try {
				    	video.requestPictureInPicture();
						$(this).text("Canvas");
					} catch(e) {
						$(this).text("Canvas...");
					}
				} else {
					document.exitPictureInPicture();
				}
			});
			$('<a href="#">').text("Fullscreen").css("font-size", "1rem").appendTo($dropdown_content).on("click", function(evt) {
				evt.preventDefault();
				this.blur();
				if($lyrics[0] != document.fullscreenElement)
					$lyrics[0].requestFullscreen();
				else
					document.exitFullscreen();
			});
			var $lines_container = $('<div class="lignes">').appendTo($lyrics);
			var $el = element.audioplayer ? $(element).parent() : $(element);
			$lyrics.insertBefore($el).append($el.detach());

			var o, lrc, $lines_list = {};
			function reinit(opt, opt_r) {
				o = $.extend(opt, {
					lyrics: $(element).attr("data-lyrics"),
					offset: $(element).attr("data-offset") || 0
				}, opt_r);
				lrc = sort_stable((is_string(o.lyrics) ? o.lyrics.split(/\r?\n|\\n/) : o.lyrics).map(function(e) {
					if(!is_string(e))
						return {t: (e.t || e.time) + o.offset, l: e.l || e.line || e.text};
					var m = e.match(/^(?:\s*\[(\d+):(\d+\.\d+)\])?\s*(.*)\s*$/);
					if(!m[1]) return {t: null, l: m[3]};
					return {t: m[1] * 60 + m[2] * 1 + o.offset, l: m[3]};
				}), function(a, b) {
					return a.t && b.t ? a.t - b.t : 0;
				});
				if(lrc[0].t)
					$lines_container.append(
						$lines_list[-1] = $("<div>")
					);
				$.each(lrc, function(index, line) {
					$lines_container.append(
						$lines_list[index] = $("<div>").attr("data-id", index).html(line.l)
					);
				});
			}
			element.lyrics = {
				"reinit": reinit,
			};
			reinit(opt, opt_r);

			var current_line_index = -1, current_line = {t: 0, l: ""};
			$(element).on("timeupdate", function() {
				var line_index = -1;
				var line = {t: 0, l: ""};
				var time = this.currentTime;
				$.each(lrc, function(index, line_to_try) {
					if(!line_to_try.t) return;
					if(line_to_try.t > time)
						return false
					line_index = index;
					line = line_to_try;
				});
				if(line_index == current_line_index) return;
				current_line_index = line_index;
				current_line = line;
				$(this).trigger("lineupdate", line, line_index);
			}).on("lineupdate", function() {
				var $active_line = $(".act", $lines_container);
				if($active_line.attr("data-id") != current_line_index) {
					$active_line.removeClass("act");
					var l = $lines_list[current_line_index].addClass("act");
					$lines_container.scrollTop((l[0].offsetTop - $lines_list[0][0].offsetTop) + l.height() / 2 - $lines_container.height() / 2);
				}

				if(canvas) {
					var ctx = canvas.getContext("2d");
					ctx.fillStyle = "white";
					ctx.fillRect(0, 0, canvas.width, canvas.height);
					ctx.fillStyle = "black";
					ctx.font = "100px sans-serif";
					ctx.textAlign = "center";
					ctx.textBaseline = "middle";

					ctx.mlFillText(current_line.l, 0, 0, canvas.width, canvas.height, "center", "center", 100);
				}
			});
		});
	}
	$.fn.lyrics = function() {
		return init(this), this;
	};
	$(function() {
		init();
	});
	return {
		init: init
	};
})();
