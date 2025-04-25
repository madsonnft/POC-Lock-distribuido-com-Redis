from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Pedido


@receiver(post_save, sender=Pedido)
def atualizar_total_pedidos(sender, instance, created, **kwargs):
    if created:
        print('atualizando total de pedidos')
        recebedor = instance.recebedor
        recebedor.total_pedidos = recebedor.pedido_set.count()
        recebedor.save()
