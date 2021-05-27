from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.db.models import Sum
from clickhouse_driver import connect

from config.celery import app
from .models import Account, Service


User = get_user_model()


@app.task
def common_balance_to_clickhouse(service_id):
    service = Service.objects.get(id=service_id)
    service_name, client_name = service.name, service.client.name
    common_balance = Account.active.filter(service=service).aggregate(Sum('balance'))['balance__sum']
    table_name = f'loyalty.{client_name}_{service_name}'
    conn = connect(
        database=settings.CLICKHOUSE['DATABASE'],
        user=settings.CLICKHOUSE['USER'],
        password=settings.CLICKHOUSE['PASSWORD'],
        host=settings.CLICKHOUSE['HOST'],
        port=settings.CLICKHOUSE['PORT']
    )
    cursor = conn.cursor()
    create_statement = """CREATE TABLE IF NOT EXISTS %s (`timestamp` DateTime, `amount` UInt64) ENGINE = Log""" % table_name
    insert_statement = """INSERT INTO %s VALUES (toDateTime(now()), toInt64(%s))""" % (table_name, common_balance)
    cursor.execute(create_statement)
    cursor.execute(insert_statement)
    conn.close()

    if common_balance >= settings.MAX_COMMON_BALANCE_VALUE:
        send_mail(
            f'Max loyalty common balance on {service_name} of {client_name}',
            f'{service_name} of {client_name} already has max loyalty common balance',
            settings.DEFAULT_FROM_EMAIL,
            [service.client.email],
            fail_silently=False,
        )


@app.task
def notify_balance(amount, customer_id, service_id):
    customer = User.objects.get(id=customer_id)
    service = Service.objects.get(id=service_id)
    client_name = service.client.name
    send_mail(
        f'Loyalty account balance on {service.name} of {client_name}',
        f'{customer.username} with email {customer.email} has {amount} balance on {service.name} of {client_name}',
        settings.DEFAULT_FROM_EMAIL,
        [service.client.email],
        fail_silently=False,
    )
