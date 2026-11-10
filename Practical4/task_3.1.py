from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
)
import time
import hashlib


def io_bound_task(url: str) -> dict:
    time.sleep(0.5)
    return {"url": url, "status": 200, "size": len(url) * 42}


def cpu_bound_task(n: int) -> dict:
    hasher = hashlib.sha256()

    for i in range(n):
        hasher.update(str(i).encode())

    return {"n": n, "hash": hasher.hexdigest()[:16]}


def risky_task(value: int) -> float:
    if value == 0:
        raise ZeroDivisionError("Ділення на нуль!")

    if value < 0:
        raise ValueError(f"Від'ємне значення: {value}")

    return 1000.0 / value


def benchmark_io_bound():
    urls = [f"https://api.example.com/data/{i}" for i in range(20)]

    start = time.perf_counter()

    sequential_results = [io_bound_task(url) for url in urls]

    sequential_time = time.perf_counter() - start

    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=5) as executor:
        parallel_results = list(executor.map(io_bound_task, urls))

    parallel_time = time.perf_counter() - start

    speedup = sequential_time / parallel_time

    print(f"Кількість задач: {len(urls)}")
    print(f"Кількість потоків: 5")
    print(f"Послідовне виконання: {sequential_time:.3f} с")
    print(f"Паралельне виконання: {parallel_time:.3f} с")
    print(f"Прискорення: {speedup:.2f}x")
    print(f"Результати збігаються: {sequential_results == parallel_results}")


def benchmark_cpu_bound():
    tasks = [500_000] * 8

    start = time.perf_counter()

    sequential_results = [cpu_bound_task(n) for n in tasks]

    sequential_time = time.perf_counter() - start

    start = time.perf_counter()

    with ProcessPoolExecutor(max_workers=4) as executor:
        parallel_results = list(executor.map(cpu_bound_task, tasks))

    parallel_time = time.perf_counter() - start

    speedup = sequential_time / parallel_time

    print(f"Кількість задач: {len(tasks)}")
    print(f"Кількість процесів: 4")
    print(f"Послідовне виконання: {sequential_time:.3f} с")
    print(f"Паралельне виконання: {parallel_time:.3f} с")
    print(f"Прискорення: {speedup:.2f}x")
    print(f"Результати збігаються: {sequential_results == parallel_results}")


def handle_exceptions():
    values = [10, 5, 0, -3, 8, 2]

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(risky_task, value): value
            for value in values
        }

        for future in as_completed(futures):
            value = futures[future]

            try:
                result = future.result()
                print(f"Значення {value}: результат = {result:.2f}")

            except ZeroDivisionError as error:
                print(f"Значення {value}: помилка — {error}")

            except ValueError as error:
                print(f"Значення {value}: помилка — {error}")


def main():
    print("=" * 60)
    print("=== I/O-bound: ThreadPoolExecutor ===")
    print("=" * 60)
    benchmark_io_bound()

    print(f"\n{'=' * 60}")
    print("=== CPU-bound: ProcessPoolExecutor ===")
    print("=" * 60)
    benchmark_cpu_bound()

    print(f"\n{'=' * 60}")
    print("=== Обробка виключень у пулах ===")
    print("=" * 60)
    handle_exceptions()


if __name__ == "__main__":
    main()