"""WSGI entrypoint for Vercel and other platforms.

This file exposes the Flask application as the variable `app` so
platforms that expect a standard name (app.py -> app) will find it.
"""
try:
    # app_simple defines `application = app` when imported as a module
    from app_simple import application as app
except Exception:
    # Fall back to importing `app` directly if present
    from app_simple import app

if __name__ == '__main__':
    # Local dev convenience
    app.run(host='0.0.0.0', port=5000)
