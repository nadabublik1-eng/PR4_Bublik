import threading
import time
import random


class BankAccount:
    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0

    def deposit(self, amount: float) -> None:
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))
        self.balance = current + amount
        self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        current = self.balance
        time.sleep(random.uniform(0.0001, 0.001))

        if current >= amount:
            self.balance = current - amount
            self.transaction_count += 1
            return True

        return False


class SafeBankAccount:
    def __init__(self, balance: float = 0.0):
        self.balance = balance
        self.transaction_count = 0
        self._lock = threading.Lock()

    def deposit(self, amount: float) -> None:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))
            self.balance = current + amount
            self.transaction_count += 1

    def withdraw(self, amount: float) -> bool:
        with self._lock:
            current = self.balance
            time.sleep(random.uniform(0.0001, 0.001))

            if current >= amount:
                self.balance = current - amount
                self.transaction_count += 1
                return True

            return False


def run_transactions(account, num_deposits: int, num_withdrawals: int):
    num_threads = 10
    barrier = threading.Barrier(num_threads)

    def worker(thread_id):
        deposits = num_deposits // num_threads
        withdrawals = num_withdrawals // num_threads

        barrier.wait()

        for _ in range(deposits):
            account.deposit(50.0)

        for _ in range(withdrawals):
            account.withdraw(50.0)

    threads = []

    for i in range(num_threads):
        thread = threading.Thread(target=worker, args=(i,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()


def main():
    initial_balance = 1000.0
    num_deposits = 100
    deposit_amount = 50.0
    num_withdrawals = 100
    withdraw_amount = 50.0

    expected_balance = (
        initial_balance
        + num_deposits * deposit_amount
        - num_withdrawals * withdraw_amount
    )

    print("Тест без синхронізації")

    unsafe_account = BankAccount(initial_balance)
    run_transactions(unsafe_account, num_deposits, num_withdrawals)

    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс: {unsafe_account.balance:.2f}")
    print(f"Кількість транзакцій: {unsafe_account.transaction_count}")
    print(f"Баланс збігається: {unsafe_account.balance == expected_balance}")

    print("\nТест із синхронізацією (Lock)")

    safe_account = SafeBankAccount(initial_balance)
    run_transactions(safe_account, num_deposits, num_withdrawals)

    print(f"Очікуваний баланс: {expected_balance:.2f}")
    print(f"Фактичний баланс: {safe_account.balance:.2f}")
    print(f"Кількість транзакцій: {safe_account.transaction_count}")
    print(f"Баланс збігається: {safe_account.balance == expected_balance}")


if __name__ == "__main__":
    main()