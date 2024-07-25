function get_upload_handler(url) {
    function upload_handler(blobInfo, progress) {
        return new Promise((success, failure) => {
            var parts = location.pathname.split("/");
            if(parts[4] == "add" && parts[5] == "") {
                failure(gettext(
                    "You must first create the item, then insert the image. "
                    + "Don't worry, the image will be uploaded after reloading."
                ));
                return;
            }
            var xhr = new XMLHttpRequest();
            xhr.open("POST", url);
            xhr.withCredentials = true;
            xhr.upload.onprogress = e => {
                progress(e.loaded / e.total * 100);
            };
            xhr.onerror = () => {
                failure("Image upload failed due to a XHR Transport error. Code: " + xhr.status);
            };
            xhr.onload = () => {
                if(xhr.status < 200 || xhr.status >= 300) {
                    failure("HTTP Error: " + xhr.status);
                    return;
                }
                var json = JSON.parse(xhr.responseText);
                if(!json || !json.location) {
                    failure("Invalid JSON: " + xhr.responseText);
                    return;
                }
                success(json.location);
            };
            var formData = new FormData();
            formData.append("file", blobInfo.blob(), blobInfo.filename());
            formData.append("csrfmiddlewaretoken", django.jQuery("#content-main form").get(0).csrfmiddlewaretoken.value);
            xhr.send(formData);
        });
    }

    return upload_handler;
}

export { get_upload_handler };
