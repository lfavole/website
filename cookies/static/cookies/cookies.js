$(function() {
    function submit(button) {
        var data = new FormData(form);
        if(button)
            data.set(button.name, button.value);
        data.set("js", 1);
        fetch($(form).attr("action"), {method: "POST", body: data})
        .then(resp => resp.json())
        .then((data) => {
            if(data.ok)
                $("#cookies").remove();
            else
                messages.error(gettext("Server error"), data.error);
        })
        .catch(err => messages.error(gettext("Error"), err));
    }

    var form = document.querySelector("#cookies form");
    $(form).on("submit", function(e) {
        e.preventDefault();
        submit();
    });
    $("button:not(.edit)", form).on("click", function(e) {
        e.preventDefault();
        submit(this);
    });

    // transform the two buttons (accept/decline) into fake buttons
    $("button[type=submit]:not([value=save])", form).attr("type", "button");

    // hide the save button and show the edit preferences button
    $("button[value=save], p:not(:last-child)", form).addClass("hidden");
    $("button.edit").removeClass("hidden").on("click", function(e) {
        // when we click on "edit preferences",
        // hide the button and show the preferences and the save button
        $(this).addClass("hidden");
        $("button[value=save], p:not(:last-child)", form).removeClass("hidden");
    });
});
