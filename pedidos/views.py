from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from pedidos.services.recipient_queue import RecipientQueue
from pedidos.tasks import processar_pedidos
import logging

logger = logging.getLogger(__name__)
queue = RecipientQueue()


class PedidoCreateView(APIView):
    def post(self, request):
        pedido_ids = request.data.get("pedido_ids")
        recebedor_id = request.data.get("recebedor_id")
        org_id = request.data.get("org_id")

        if not recebedor_id or not org_id or not pedido_ids:
            return Response({"erro": "Campos obrigatórios"}, status=status.HTTP_400_BAD_REQUEST)

        queue.add_item(org_id, recebedor_id, pedido_ids)
        processar_pedidos.delay(org_id, recebedor_id)

        return Response({"mensagem": "Pedido enfileirado"}, status=status.HTTP_202_ACCEPTED)

