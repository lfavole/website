import tinyMCE from "https://cdn.jsdelivr.net/npm/tinymce@7/+esm";
import "https://cdn.jsdelivr.net/npm/tinymce@7/icons/default/icons.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/themes/silver/theme.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/models/dom/model.min.js";
import "https://cdn.tiny.cloud/1/no-api-key/tinymce/7/langs/fr_FR.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/autolink/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/code/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/fullscreen/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/help/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/image/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/link/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/lists/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/media/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/preview/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/quickbars/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/save/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/searchreplace/plugin.min.js";
import "https://cdn.jsdelivr.net/npm/tinymce@7/plugins/table/plugin.min.js";

import get_upload_handler from "./upload_handler.js";

function initTinyMCE(el) {
    if (el.closest(".empty-form") !== null)  // Don't do empty inlines
        return
    var mce_conf = JSON.parse(el.dataset.mceConf);
    mce_conf.images_upload_handler = get_upload_handler(mce_conf.upload_image_url);

    // There is no way to pass a JavaScript function as an option
    // because all options are serialized as JSON.
    const fns = [
        "color_picker_callback",
        "file_browser_callback",
        "file_picker_callback",
        "images_dataimg_filter",
        "images_upload_handler",
        "paste_postprocess",
        "paste_preprocess",
        "setup",
        "urlconverter_callback",
    ];
    fns.forEach((fn_name) => {
        if (typeof mce_conf[fn_name] == "undefined")
            return;
        if (mce_conf[fn_name].includes("("))
            mce_conf[fn_name] = eval("(" + mce_conf[fn_name] + ")");
        else
            mce_conf[fn_name] = window[mce_conf[fn_name]];
    });

    if("protect" in mce_conf)
        mce_conf["protect"] = mce_conf["protect"].map(function(item) {
            var match = /^\/(.*)\/([gimuy]*)$/.exec(item);
            if(match === null)
                return new RegExp(item);
            else
                return new RegExp(match[1], match[2]);
        });

    if (!"selector" in mce_conf)
        mce_conf["target"] = el;
    if (!tinyMCE.get(el.id))
        tinyMCE.init(mce_conf);
}

function initializeTinyMCE(element, formsetName) {
    django.jQuery(".tinymce", element).each((_index, element) => initTinyMCE(element));
}

django.jQuery(function($) {
    if (!tinyMCE)
        throw "tinyMCE is not loaded. If you customized TINYMCE_JS_URL, double-check its content.";
    // initialize the TinyMCE editors on load
    initializeTinyMCE(document);

    // initialize the TinyMCE editor after adding an inline in the django admin context.
    $(document).on("formset:added", (event, $row, formsetName) => {
        if (event.detail && event.detail.formsetName)
            // Django >= 4.1
            initializeTinyMCE(event.target);
        else
            // Django < 4.1, use $row
            initializeTinyMCE($row.get(0));
    });
});
