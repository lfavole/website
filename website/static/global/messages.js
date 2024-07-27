var messages = window.messages = {
    container: null,
    list: [],
    add: function(title, text, type = "", persistent = true) {
        var msg = $("<li>").addClass(type).toogleClass("persistent", persistent);
        if(title)
            msg.append($("<b>").text(title)).append("<br>");
        msg.append($("<span>").text(text));
        msg.appendTo(this.container);
        return this._setup(msg);
    },
    debug: function(title, text, persistent = True) {
        this.add(title, text, "debug", persistent);
    },
    info: function(title, text, persistent = True) {
        this.add(title, text, "info", persistent);
    },
    warning: function(title, text, persistent = True) {
        this.add(title, text, "warning", persistent);
    },
    error: function(title, text, persistent = True) {
        this.add(title, text, "error", persistent);
    },
    _remove: function(msg) {
        msg.addClass("removing");
        setTimeout(() => msg.remove(), 400);
    },
    _setup: function(msg) {
        var msg = $(msg);
        var _remove = this._remove;
        var disappear_timeout;
        var disappearing = true;
        var pinned = false;

        function update_disappear(val) {
            if(typeof val == "boolean")
                disappearing = val;
            if(disappearing && !pinned) {
                msg.addClass("disappearing");
                disappear_timeout = setTimeout(() => _remove(msg), 5000);
            } else {
                msg.removeClass("disappearing");
                clearTimeout(disappear_timeout);
            }
        }
        function update_pin(val) {
            pinned = val;
            update_disappear();
        }

        if(!msg.is(".persistent")) {
            msg.on("mouseenter", () => update_disappear(false));
            msg.on("mouseleave", () => update_disappear(true));
            update_disappear();

            msg.prepend(
                $('<a href="#" class="pin">')
                .on("click", (e) => {e.preventDefault(); update_pin(!pinned);})
            );
        }

        msg.prepend(
            $('<a href="#" class="close">')
            .on("click", (e) => {e.preventDefault(); _remove(msg)})
        );

        return {
            update_disappear: update_disappear,
            update_pin: update_pin,
        }
    },
};

$(function() {
    messages.container = $(".messagelist");
    $(".messagelist li").each((i, e) => {messages.list.push(e); messages._setup(e);});
})
