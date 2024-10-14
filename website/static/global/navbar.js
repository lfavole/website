// https://github.com/lukejacksonn/GreedyNav

$(function() {
    var $nav = $("nav");
    var $btn = $("nav .navbar-burger");
    var $vlinks = $("nav > ul:first-of-type");
    var $hlinks = $("nav > ul:last-of-type");

    var numOfItems = 0;
    var totalSpace = 0;
    var breakWidths = [];

    // Get initial state
    $vlinks.children().each(function(i, e) {
        totalSpace += $(e).outerWidth();
        numOfItems += 1;
        breakWidths.push(totalSpace);
    });

    var availableSpace, numOfVisibleItems = 0, requiredSpace;

    function check() {
        // Avoid an infinite loop
        while(numOfVisibleItems >= 0) {
            // Get instant state
            availableSpace = $nav.width() - $btn.width();
            numOfVisibleItems = $vlinks.children().length;
            requiredSpace = breakWidths[numOfVisibleItems - 1];

            // There is not enough space
            if (requiredSpace > availableSpace) {
                $vlinks.children().last().prependTo($hlinks);
                numOfVisibleItems -= 1;
                continue;
            } else if (availableSpace > breakWidths[numOfVisibleItems]) {
                // There is more than enough space
                $hlinks.children().first().appendTo($vlinks);
                numOfVisibleItems += 1;
                continue;
            }
            break;
        }
        // Update the button accordingly
        $btn.toggleClass("hidden", numOfVisibleItems === numOfItems);
        $hlinks.css("right", $("body").width() - ($btn.position().left + $btn.width()));
        $hlinks.css("top", $btn.position().top);
    }

    // Window listeners
    $(window).resize(check);

    check();
});
