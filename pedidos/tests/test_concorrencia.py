import pytest
import fakeredis
from threading import Thread
from pedidos.models import Recebedor, Pedido
from pedidos.services.recipient_queue import RecipientQueue
from pedidos.tasks import processar_pedidos


@pytest.fixture
def redis_mock(monkeypatch):
    """
    Substitui a conexão Redis por uma versão fake para testes
    """
    r = fakeredis.FakeStrictRedis(decode_responses=True)
    monkeypatch.setattr(
        "pedidos.services.recipient_queue.redis.Redis.from_url",
        lambda *a, **kw: r
    )
    return r


@pytest.mark.django_db
def test_concorrencia_simples(redis_mock):
    """
    Simula múltiplas tasks concorrentes processando pedidos da mesma fila.
    Apenas uma task deve processar tudo com exclusividade.
    """
    org_id = 77
    recebedor = Recebedor.objects.create(nome="Concorrente", org=org_id)
    pedidos = [str(i) for i in range(10)]

    fila = RecipientQueue()
    fila.add_item(org_id, recebedor.id, pedidos)

    def run_task():
        processar_pedidos.apply(args=(org_id, recebedor.id))

    threads = [Thread(target=run_task) for _ in range(5)]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert Pedido.objects.filter(recebedor=recebedor, org=org_id).count() == 10
    recebedor.refresh_from_db()
    assert recebedor.total_pedidos == 10
    assert redis_mock.llen(fila.get_queue_key(org_id, recebedor.id)) == 0
    assert redis_mock.get(fila.get_lock_key(org_id, recebedor.id)) is None
