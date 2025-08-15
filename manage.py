#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')
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
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_project.settings')

    # ✅ Setup Django before accessing models
    import django
    django.setup()

    if os.environ.get('RENDER') and os.environ.get('CREATE_SUPERUSER') == 'True':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        if not User.objects.filter(username=os.environ['DJANGO_SUPERUSER_USERNAME']).exists():
            User.objects.create_superuser(
                username=os.environ['DJANGO_SUPERUSER_USERNAME'],
                email=os.environ['DJANGO_SUPERUSER_EMAIL'],
                password=os.environ['DJANGO_SUPERUSER_PASSWORD']
            )

    main()
