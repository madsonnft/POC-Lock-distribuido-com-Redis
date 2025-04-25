from typing import List

import redis

from pedidos.services.base_queue import BaseQueue


class RecipientQueue(BaseQueue):
    def __init__(self, redis_url="redis://redis:6379/0"):
        self.redis = redis.Redis.from_url(redis_url, decode_responses=True)

    def get_base_key(self, org_id, recipient_id):
        return f"pedidos_recebedor:org:{org_id}:recipient:{recipient_id}"

    def get_queue_key(self, org_id, recipient_id):
        return f"{self.get_base_key(org_id, recipient_id)}:fila"

    def get_lock_key(self, org_id, recipient_id):
        return f"{self.get_base_key(org_id, recipient_id)}:lock"

    def add_item(self, org_id: int, recipient_id: int, payable_ids: List[str]) -> None:
        queue_key = self.get_queue_key(org_id, recipient_id)
        if payable_ids:
            self.redis.rpush(queue_key, *[str(pid) for pid in payable_ids])

    def pop_all(self, org_id, recipient_id) -> list:
        items = []
        while True:
            item = self.redis.lpop(self.get_queue_key(org_id, recipient_id))
            if item is None:
                break
            items.append(item)
        return items

    def is_empty(self, org_id, recipient_id) -> bool:
        return self.redis.llen(self.get_queue_key(org_id, recipient_id)) == 0

    def clear_queue(self, org_id: int, recipient_id: int) -> None:
        self.redis.delete(self.get_queue_key(org_id, recipient_id))
