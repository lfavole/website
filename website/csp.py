class InvalidCSPError(ValueError):
    """Error in the CSP dict."""


CSP_FETCH_SPECIAL = ("self", "none", "unsafe-inline", "unsafe-eval", "strict-dynamic")

CSP_PREFIX_SPECIAL = ("nonce-", "sha256-", "sha384-", "sha512-")

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
            elif value in CSP_FETCH_SPECIAL or value.startswith(CSP_PREFIX_SPECIAL):
                values.append(f"'{value}'")
            else:
                values.append(value)
        return " ".join(values)

    pieces = []
    for name, value in csp.items():
        if name not in CSP_SCHEMA:
            raise InvalidCSPError(f"Unknown directive: {name}")

        types, values = CSP_SCHEMA[name]

        types = (list, tuple, set) if types is list else (types,)

        if not isinstance(value, types):
            raise InvalidCSPError(f"Values for {name} must be {types[0].__name__} type, not {type(value).__name__}")

        # skip some parameters used by the middleware
        if not value or name in ("report-only", "report-threshold"):
            continue

        if values and value not in values:
            raise InvalidCSPError(f"Unknown {name} value: {value}")

        if types[0] is bool:
            pieces.append(name)
            continue

        if types[0] is list:
            pieces.append(f"{name} {compile_list(value)}")
            continue

        pieces.append(f"{name} {value}")

    return "; ".join(pieces)
