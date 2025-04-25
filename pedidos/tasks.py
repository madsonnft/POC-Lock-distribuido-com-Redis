from celery import shared_task
from django.db import transaction

from pedidos.services.recipient_queue import RecipientQueue
from pedidos.utils.celery_lock import unique_queue_task
from pedidos.models import Pedido, Recebedor
import os
import django
import logging
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "recebedores.settings")
django.setup()
logger = logging.getLogger(__name__)


@shared_task(bind=True, queue='pedidos_recebedor')
@unique_queue_task(queue_interface=RecipientQueue)
def processar_pedidos(payables, org_id, recipient_id):
    if payables:
        logger.info(f"[PROCESSING] Found {len(payables)} orders for {org_id}/{recipient_id}")
        criar_ou_editar_antecipacao(org_id, recipient_id, payables)
    else:
        logger.info(f"[PROCESSING] No payables found in queue for {org_id}/{recipient_id}")


def criar_ou_editar_antecipacao(org_id, recipient_id, payables: list):
    with transaction.atomic():
        exists_recebedor = Recebedor.objects.filter(codigo=str(recipient_id), org=org_id).exists()
        if not exists_recebedor:
            logger.info(f"[ANTICIPATION] Create anticipation for recipient {org_id}/{recipient_id} with {len(payables)} payables")
            Recebedor.objects.create(
                nome=str(recipient_id),
                codigo=str(recipient_id),
                org=str(org_id),
            )
            time.sleep(30)

        recebedor = Recebedor.objects.select_for_update().get(codigo=str(recipient_id), org=org_id)
        list_payables = []
        for payable in payables:
            list_payables.append(
                Pedido(
                    recebedor_id=recebedor.id,
                    codigo=str(payable),
                    org=str(org_id),
                )
            )

        if list_payables:
            logger.info(f"[ANTICIPATION] Updating anticipation for recipient {org_id}/{recipient_id} with order {len(list_payables)} payables")
            time.sleep(3)
            Pedido.objects.bulk_create(list_payables)

            # Atualiza o total de pedidos após o bulk_create
            total = Pedido.objects.filter(recebedor_id=recebedor.id, org=org_id).count()
            recebedor.total_pedidos = total
            recebedor.save(update_fields=["total_pedidos"])
