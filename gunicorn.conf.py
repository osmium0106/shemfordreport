# Production WSGI configuration
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 120
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 60

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "student_report_app"

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190