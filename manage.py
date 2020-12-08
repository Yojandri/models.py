#!/usr/bin/python
# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoProject.settings")  # project_name 项目名称
django.setup()


#  设置项目的X-Frame-Options（这玩意儿是啥我也没搞懂自己百度）为sameorigin保证页面就可以在同域名页面的 frame 中嵌套，就是弹窗弹出来不会被拒绝
X_FRAME_OPTIONS = 'SAMEORIGIN'


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoProject.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
