from django import forms

BASE_URL = "https://cdn.jsdelivr.net/npm/codemirror@5"


class MarkdownEditor(forms.Textarea):
    """
    Markdown editor for pages and articles.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs["class"] = "html-editor"
        self.attrs["style"] = "width: 90%; height: 100%;"

    class Media:
        css = {
            "all": (
                BASE_URL + "/lib/codemirror.min.css",
                BASE_URL + "/theme/mdn-like.min.css",
            ),
        }
        js = (
            BASE_URL + "/lib/codemirror.min.js",
            BASE_URL + "/mode/markdown/markdown.min.js",
            BASE_URL + "/mode/xml/xml.min.js",
            "/static/codemirror/codemirror-init.js",
        )
