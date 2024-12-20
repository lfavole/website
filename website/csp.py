from django.views import debug

from .decorators import csp

class InvalidCSPError(ValueError):
    """Error in the CSP dict."""


# special keywords that must be surrounded by quotes
CSP_FETCH_SPECIAL = ("self", "none", "unsafe-inline", "unsafe-eval", "strict-dynamic")

# special prefixes which say that the text must be surrounded by quotes
CSP_PREFIX_SPECIAL = ("nonce-", "sha256-", "sha384-", "sha512-")

# data sources (xxx-src directives) that can be used in templates or views
CSP_SOURCES = (
    "connect",
    "child",
    "default",
    "font",
    "frame",
    "img",
    "manifest",
    "media",
    "object",
    "script",
    "style",
    "worker",
)

# types and possible values of all CSP directives
CSP_SCHEMA: dict[str, tuple[type, None | set[str]]] = {
    ## Lists
    # Fetch directives:
    "connect-src": (list, None),
    "child-src": (list, None),
    "default-src": (list, None),
    "font-src": (list, None),
    "frame-src": (list, None),
    "img-src": (list, None),
    "manifest-src": (list, None),
    "media-src": (list, None),
    "object-src": (list, None),
    "script-src": (list, None),
    "style-src": (list, None),
    "worker-src": (list, None),
    # Navigation directives:
    "form-action": (list, None),
    "frame-ancestors": (list, None),
    # Document directives:
    "base-uri": (list, None),
    "plugin-types": (list, None),
    ## Other directives
    "block-all-mixed-content": (bool, None),
    "report-uri": (str, None),
    "require-sri": (
        str,
        {
            "script",
            "style",
            "script style",
        },
    ),
    "sandbox": (
        list,
        {
            "allow-forms",
            "allow-modals",
            "allow-orientation-lock",
            "allow-pointer-lock",
            "allow-popups",
            "allow-popups-to-escape-sandbox",
            "allow-presentation",
            "allow-same-origin",
            "allow-scripts",
            "allow-top-navigation",
        },
    ),
    "upgrade-insecure-requests": (bool, None),
    ## App parameters
    "report-only": (bool, None),
    "report-threshold": (float, None),
}


def compile_csp(csp: dict | str):
    """Transform a CSP dict into a CSP string."""

    # skip the compilation for already formatted CSPs
    if isinstance(csp, str):
        return csp

    def compile_list(value_list):
        values = []
        for value in value_list:
            if value is None:
                values.append("'none'")
            elif value in CSP_FETCH_SPECIAL or str(value).startswith(CSP_PREFIX_SPECIAL):
                values.append(f"'{value}'")
            else:
                values.append(value)
        return " ".join(str(x) for x in values)

    pieces = []
    for name, value in csp.items():
        # raise for invalid CSP directives
        if name not in CSP_SCHEMA:
            raise InvalidCSPError(f"Unknown directive: {name + ': ' + value!r}")

        types, values = CSP_SCHEMA[name]

        LIST_TYPES = (list, tuple, set)
        types = LIST_TYPES if types is list else (types,)

        if not isinstance(value, types):
            raise InvalidCSPError(f"Values for {name} must be {types[0].__name__} type, not {type(value).__name__}")

        # skip some parameters used by the middleware
        if not value or name in ("report-only", "report-threshold"):
            continue

        if types[0] is bool:
            pieces.append(name)
            continue

        # raise for invalid values
        value_list = value if isinstance(value, LIST_TYPES) else [value]
        if values:
            for value_item in value_list:
                if value_item not in values:
                    raise InvalidCSPError(f"Unknown {name} directive: {value_item!r}")

        if types[0] is list:
            pieces.append(f"{name} {compile_list(value)}")
            continue

        pieces.append(f"{name} {value}")

    return "; ".join(pieces)

_apply_csp = csp({"style-src": ["unsafe-inline"], "script-src": ["unsafe-inline"]})
debug.technical_404_response = _apply_csp(debug.technical_404_response)
debug.technical_500_response = _apply_csp(debug.technical_500_response)
