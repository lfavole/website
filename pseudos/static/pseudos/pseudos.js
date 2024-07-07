$(function() {
    mots = $("textarea[name=mots]")
    ajouter_mot = function(mot) {
        mots.val(mots.val() + "\n" + mot)
    };
    $(".derniers-mots li").click(function() {
        ajouter_mot($(this).text())
    });
    $("aside img").click(function() {
        ajouter_mot($(this).attr("alt"))
    });
});