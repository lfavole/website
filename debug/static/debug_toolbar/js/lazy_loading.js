import { ajax } from "./utils.js";


function load() {
    var djDebugData = document.getElementById("djDebug").dataset;
    var sidebarUrl = djDebugData.sidebarUrl;
    var storeId = encodeURIComponent(djDebugData.storeId);

    ajax(`${sidebarUrl}?store_id=${storeId}`).then(function(data) {
        Object.keys(data).forEach(function(panelId) {
            var panelElement = document.createElement("div");
            document.getElementById("djDebug").insertBefore(panelElement, document.getElementById("djDebugWindow"));
            panelElement.outerHTML = data[panelId].content;

            var buttonElement = document.createElement("li");
            document.getElementById("djDebugPanelList").appendChild(buttonElement);
            buttonElement.outerHTML = data[panelId].button;
        });
    });
}

function init() {
    if(localStorage.getItem("djdt.show") == "true") {
        load();
        return;
    }
    var button = document.getElementById("djShowToolBarButton");
    function buttonClick() {
        button.removeEventListener("click", buttonClick);
        load();
    }
    button.addEventListener("click", buttonClick);
}

if(document.readyState !== "loading")
    init();
else
    document.addEventListener("DOMContentLoaded", init);
