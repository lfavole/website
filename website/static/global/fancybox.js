$(function() {
    function add_fancybox() {
        $('<link rel="stylesheet">')
        .attr("src", navigator.onLine ? "https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.css" : "/static/vendor/fancybox.css")
        .appendTo("head");
        $.getScript("https://cdn.jsdelivr.net/npm/@fancyapps/ui@5/dist/fancybox/fancybox.umd.js")
        .done(function() {
            console.log($("img"));
            Fancybox.bind("main img", {
                "groupAll": true,
                "Slideshow": {
                    "timeout": 7000,
                },
                "Thumbnails": {
                    "showOnStart": false,
                },
            });
        });
    }

    if($("main img").length) {
        add_fancybox();
    } else {
        var $main = $("main")[0];
        if($main) {
            var mo = new MutationObserver(function() {
                mo.disconnect();
                add_fancybox();
            });
            mo.observe($main, {"childList": "img"});
        }
    }
});
