import os
import sys
import importlib


__all__ = ['config']


def _get_config():
    try:
        module = importlib.import_module(f'api.config.base')
        settings = {k: v for k, v in vars(module).items(
        ) if not k.startswith('_') and k.isupper()}
        return settings
    except Exception:
        sys.stderr.write('Failed to read config file: config.base.py')
        sys.stderr.flush()
        raise


config = _get_config()
