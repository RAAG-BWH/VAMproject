CSP_POLICY = {
    'default-src': "'self'",
    'script-src': "'self' 'unsafe-inline' 'unsafe-eval'",
    'connect-src': "'self' https://127.0.0.1:8000",
    'frame-src': "'self' https://127.0.0.1:8000",
    'img-src': "'self' data:",
}


def csp_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        for key, value in CSP_POLICY.items():
            response["Content-Security-Policy"] = f"{key} {value};"
        return response
    return middleware