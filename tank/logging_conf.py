def build_logging_conf(logs_dir: str) -> dict:
    """Builds dict logging config."""
    logging_conf = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': '%(asctime)s %(name)s(%(lineno)d) - %(levelname)s: %(message)s',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'WARNING',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
            'info_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'simple',
                'filename': logs_dir,  # TODO build with user_dir()
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 3,
                'encoding': 'utf8',
            },
            'error_file_handler': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'simple',
                'filename': logs_dir,  # TODO build with user_dir()
                'maxBytes': 10 * 1024 * 1024,  # 10 MB
                'backupCount': 3,
                'encoding': 'utf8',
            },
        },
        'root': {
            'level': 'DEBUG',
            'handlers': ['console', 'info_file_handler', 'error_file_handler'],
        },
    }

    return logging_conf
