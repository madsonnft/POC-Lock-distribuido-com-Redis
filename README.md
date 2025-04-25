# Arquitetura de Processamento com Fila por Recebedor e Lock Redis

Este projeto usa uma arquitetura escalável para processar pedidos com base em **fila por recebedor** e controle de concorrência via **lock distribuído no Redis**.

---

## 🧱 Visão Geral da Arquitetura

- Cada recebedor possui uma **fila própria** no Redis (ex: `recebedor:{id}:fila`)
- Um **lock exclusivo por recebedor** (`SET recebedor:{id}:lock NX EX 300`) garante que apenas **um worker por recebedor** processe os pedidos.
- As tasks são executadas de forma assíncrona com **Celery + Redis**, usando a fila nomeada `pedidos_recebedor`.

---

## ✅ Por que essa arquitetura é robusta?

Esta arquitetura é compatível com sistemas de alto volume financeiro (ex: R$ 100 milhões/dia), desde que siga as boas práticas abaixo:

| Requisito | Descrição |
|----------|-----------|
| ✔ Lock com TTL | Garante que travas não fiquem presas caso um worker morra |
| ✔ Verificação de fila antes de liberar o lock | Evita condições de corrida entre workers |
| ✔ Task idempotente | Garante que reexecuções não causem erros ou duplicações |
| ✔ Fila por chave lógica (recebedor) | Aumenta a paralelização e evita conflitos |

---

## ⚠️ Riscos conhecidos e como mitigar

### Lock expira no meio do processamento
- **Risco**: outro worker pode assumir a fila enquanto o anterior ainda está rodando
- **Solução**: renovar TTL com `EXPIRE` a cada iteração

### Fila esquecida após lock ser liberado
- **Risco**: se o lock for deletado logo após um novo `rpush`, a task pode não ser reexecutada
- **Solução**: usar `LLEN` ou script Lua para garantir atomicidade

---

## 🧠 Termos técnicos aplicáveis

- **Redis Distributed Lock**
- **Sharded Queue**
- **Single-Consumer FIFO per Key**
- **Task Coalescing Pattern**
- **Queue Partitioning**

---

## 🔧 Sugestões de melhorias futuras

- Usar **PostgreSQL advisory locks** para locks transacionais
- Substituir Redis por **Kafka com chave por recebedor**
- Implementar **Redlock** se tiver Redis distribuído multi-host
- Criar uma task `flush_pedidos_por_recebedor` que batcha por tempo

---

## 📦 Fila usada

Todas as tasks de pedidos são roteadas para:

```
Fila: pedidos_recebedor
```

Configurado em `settings.py`:

```python
CELERY_TASK_ROUTES = {
    'pedidos.tasks.processar_pedidos': {
        'queue': 'pedidos_recebedor',
    }
}
```
