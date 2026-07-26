from app import app  # Ensure 'app' matches your main Flask file name (e.g., app.py)
import serverless_wsgi


def handler(event, context):
  return serverless_wsgi.handle_request(app, event, context)
