import threading
import queue
import time
import random


class Task:
    def __init__(self, task_id: int, data: str, priority: int = 0):
        self.task_id = task_id
        self.data = data
        self.priority = priority
        self.created_at = time.time()

    def __repr__(self):
        return f"Task(id={self.task_id}, data='{self.data}')"


def producer(task_queue: queue.Queue, num_tasks: int,
             producer_id: int) -> None:

    for i in range(num_tasks):
        task = Task(
            task_id=producer_id * 100 + i,
            data=f"Дані від виробника {producer_id}, пакет {i}",
            priority=random.randint(1, 5),
        )

        task_queue.put(task)

        print(f"[Виробник-{producer_id}] Створено {task}")

        time.sleep(random.uniform(0.1, 0.3))

    print(f"[Виробник-{producer_id}] Завершив роботу")


def consumer(task_queue: queue.Queue, consumer_id: int,
             results: list, results_lock: threading.Lock) -> None:

    while True:
        try:
            task = task_queue.get(timeout=2)

        except queue.Empty:
            print(f"[Споживач-{consumer_id}] Очікування задач...")
            continue

        if task is None:
            task_queue.task_done()
            print(f"[Споживач-{consumer_id}] Завершив роботу")
            break

        try:
            start = time.perf_counter()

            work_time = random.uniform(0.1, 0.4)
            time.sleep(work_time)

            processing_time = time.perf_counter() - start

            with results_lock:
                results.append({
                    "task_id": task.task_id,
                    "consumer_id": consumer_id,
                    "processing_time": processing_time,
                })

            print(
                f"[Споживач-{consumer_id}] Оброблено задачу "
                f"{task.task_id} за {processing_time:.2f} с"
            )

        finally:
            task_queue.task_done()


def producer_consumer_demo():
    task_queue = queue.Queue(maxsize=5)
    results = []
    results_lock = threading.Lock()

    num_producers = 2
    num_consumers = 3
    tasks_per_producer = 5

    producers = []
    consumers = []

    for i in range(num_consumers):
        t = threading.Thread(
            target=consumer,
            args=(task_queue, i, results, results_lock),
        )
        consumers.append(t)
        t.start()

    for i in range(num_producers):
        t = threading.Thread(
            target=producer,
            args=(task_queue, tasks_per_producer, i),
        )
        producers.append(t)
        t.start()

    for t in producers:
        t.join()

    for _ in range(num_consumers):
        task_queue.put(None)

    task_queue.join()

    for t in consumers:
        t.join()

    total_tasks = len(results)

    average_time = (
        sum(r["processing_time"] for r in results) / total_tasks
        if total_tasks > 0 else 0
    )

    print("\n=== Результати Producer-Consumer ===")
    print(f"Кількість виробників: {num_producers}")
    print(f"Кількість споживачів: {num_consumers}")
    print(f"Максимальний розмір черги: {task_queue.maxsize}")
    print(f"Створено задач: {num_producers * tasks_per_producer}")
    print(f"Оброблено задач: {total_tasks}")
    print(f"Середній час обробки: {average_time:.3f} с")
    print(f"Усі задачі оброблено: {total_tasks == num_producers * tasks_per_producer}")


def deadlock_demo():
    lock_a = threading.Lock()
    lock_b = threading.Lock()
    deadlock_detected = threading.Event()
    barrier = threading.Barrier(2)

    def worker_1():
        with lock_a:
            print("[Worker-1] Захопив Lock A")

            barrier.wait()

            acquired = lock_b.acquire(timeout=2)

            if not acquired:
                print("[Worker-1] ДЕДЛОК: не вдалося захопити Lock B!")
                deadlock_detected.set()
                return

            try:
                print("[Worker-1] Захопив Lock B")
            finally:
                lock_b.release()

    def worker_2():
        with lock_b:
            print("[Worker-2] Захопив Lock B")

            barrier.wait()

            acquired = lock_a.acquire(timeout=2)

            if not acquired:
                print("[Worker-2] ДЕДЛОК: не вдалося захопити Lock A!")
                deadlock_detected.set()
                return

            try:
                print("[Worker-2] Захопив Lock A")
            finally:
                lock_a.release()

    def safe_worker_1():
        with lock_a:
            print("[Safe-Worker-1] Захопив Lock A")

            time.sleep(0.1)

            with lock_b:
                print("[Safe-Worker-1] Захопив Lock B")
                print("[Safe-Worker-1] Роботу завершено")

    def safe_worker_2():
        with lock_a:
            print("[Safe-Worker-2] Захопив Lock A")

            time.sleep(0.1)

            with lock_b:
                print("[Safe-Worker-2] Захопив Lock B")
                print("[Safe-Worker-2] Роботу завершено")

    print("=== Спроба з потенційним дедлоком ===")

    t1 = threading.Thread(target=worker_1)
    t2 = threading.Thread(target=worker_2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    if deadlock_detected.is_set():
        print("Дедлок виявлено! Timeout запобіг зависанню.")
    else:
        print("Дедлок не виник.")

    print("\n=== Безпечна версія ===")

    t3 = threading.Thread(target=safe_worker_1)
    t4 = threading.Thread(target=safe_worker_2)

    t3.start()
    t4.start()

    t3.join()
    t4.join()

    print("Безпечна версія завершена без дедлоку.")


def main():
    print("=" * 60)
    print("=== Паттерн Producer-Consumer ===")
    print("=" * 60)

    producer_consumer_demo()

    print(f"\n{'=' * 60}")
    print("=== Демонстрація дедлоку ===")
    print("=" * 60)

    deadlock_demo()


if __name__ == "__main__":
    main()