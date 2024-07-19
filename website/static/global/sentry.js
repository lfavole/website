import * as Sentry from "https://cdn.jsdelivr.net/npm/@sentry/browser/+esm";

function makeFetchTransport(options) {
    var token = "";
    window.addEventListener("DOMContentLoaded", function() {
        var element = document.querySelector("input[name=csrfmiddlewaretoken]");
        if(element)
            token = element.value;
    });

    function makeRequest(request) {
        var requestOptions = {
            body: request.body,
            method: "POST",
            referrerPolicy: "origin",
            headers: {
                ...options.headers,
                "X-CSRFToken": token,
            },
            ...options.fetchOptions,
        };

        return fetch(options.url, requestOptions).then(response => {
            return {
                statusCode: response.status,
                headers: {
                    "x-sentry-rate-limits": response.headers.get("X-Sentry-Rate-Limits"),
                    "retry-after": response.headers.get("Retry-After"),
                },
            };
        });
    }

    return Sentry.createTransport(options, makeRequest);
}

Sentry.init({
    dsn: "",
    tunnel: "/sentry",
    integrations: [
        Sentry.browserTracingIntegration(),
        Sentry.replayIntegration(),
        Sentry.replayCanvasIntegration(),
    ],
    transport: makeFetchTransport,
    tracesSampleRate: 0.1,
    replaysSessionSampleRate: 0.1,
    replaysOnErrorSampleRate: 1.0,
});
