"""
Celery config, schedule
"""

from celery.schedules import crontab
broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'
result_backend_transport_options = {'visibility_timeout': 18000}
# task_soft_limit = 3600
# task_hard_limit = 7200
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
enable_utc = False
worker_hijack_root_logger = False
worker_redirect_stdouts = False
worker_max_tasks_per_child = 10
task_ignore_result = True
task_routes = {
    'crusoe.*': {'queue': 'crusoe'},
}
beat_schedule = {
    'sabu': {
        'task': 'crusoe.sabu',
        'schedule': 300,
    },
    'NETlist': {
        'task': 'crusoe.netlist',
        'schedule': 3600,
    },
    'rtir-connector': {
        'task': 'crusoe.rtir_connector',
        'schedule': 3600,
    },
    'cleaner': {
        'task': 'crusoe.cleaner',
        'schedule': 1200,
    },
    'cms-scan': {
        'task': 'crusoe.cms_scan',
        'schedule': 43200,
    },
    'flowmon': {
        'task': 'crusoe.flowmon_chain',
        'schedule': crontab(minute='*/5'),
    },
    'shodan': {
        'task': 'crusoe.shodan',
        'schedule': crontab(hour=19, minute=0),
    },
    'check_certs': {
        'task': 'crusoe.check_certs',
        'schedule': crontab(hour=21, minute=0),
    },
    'compute_criticality': {
        'task': 'crusoe.compute_criticality',
        'schedule': crontab(hour=22, minute=48),
    },
    'nvd-cve': {
        'task': 'crusoe.nvd_CVEs',
        'schedule': crontab(hour=22, minute=0),
    },
    'vendor-cve': {
        'task': 'crusoe.vendor_CVEs',
        'schedule': crontab(hour=22, minute=10),
    },
    'shadow-server': {
        'task': 'crusoe.shadowserver',
        'schedule': crontab(hour=23, minute=0),
    }
}
