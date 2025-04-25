# pedidos/models.py

from django.db import models


class Recebedor(models.Model):
    nome = models.CharField(max_length=255)
    org = models.CharField(max_length=255)
    codigo = models.CharField(max_length=255)
    total_pedidos = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['org', 'codigo'], name='unique_org_codigo')
        ]


class Pedido(models.Model):
    org = models.CharField(max_length=255)
    recebedor = models.ForeignKey(Recebedor, on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255)
    criado_em = models.DateTimeField(auto_now_add=True)
