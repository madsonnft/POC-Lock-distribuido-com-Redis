import logging
from functools import wraps
from celery import Task

logger = logging.getLogger(__name__)


def unique_queue_task(queue_interface, lock_ttl=120):
    def decorator(task_func):
        @wraps(task_func)
        def wrapper(self: Task, *args, **kwargs):
            queue = queue_interface()
            base_key = queue.get_base_key(*args, **kwargs)
            lock_key = queue.get_lock_key(*args, **kwargs)

            lock = queue.redis.set(lock_key, "1", nx=True, ex=lock_ttl)
            if not lock:
                logger.info(f"[LOCK] Lock already in use for {base_key}")
                return

            try:
                logger.info(f"[LOCK] Lock acquired for {base_key}")

                while True:
                    items = queue.pop_all(*args, **kwargs)

                    if not items:
                        logger.info(f"[QUEUE] No items to process for {base_key}")
                        break

                    logger.info(f"[QUEUE] Processing {len(items)} items from {base_key}")
                    task_func(items, *args, **kwargs)
                    queue.redis.expire(lock_key, lock_ttl)

                if queue.is_empty(*args, **kwargs):
                    logger.info(f"[LOCK] Queue is empty. Releasing lock for {base_key}")
                    queue.redis.delete(lock_key)
                else:
                    logger.info(f"[REQUEUE] Queue still has items. Rescheduling task for {base_key}")
                    self.apply_async(args=args, kwargs=kwargs, countdown=2)

            except Exception as e:
                logger.error(f"[unique_queue_task] Error while processing {base_key}: {e}")
                raise
        return wrapper
    return decorator
