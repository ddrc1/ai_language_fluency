from celery import shared_task

from apps.cron.cron import generate_email_content


@shared_task
def send_exercice_email():
    generate_email_content()
