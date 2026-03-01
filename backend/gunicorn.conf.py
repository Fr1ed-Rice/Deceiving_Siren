# Gunicorn configuration file
import multiprocessing

# Bind to port 5000
bind = "0.0.0.0:5000"

# Workers
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"

# Timeout (300s for large file processing)
timeout = 300
graceful_timeout = 30

# Request limits
limit_request_body = 83886080  # 80MB

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
