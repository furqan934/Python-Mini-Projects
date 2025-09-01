"""
ATM Machine – Mini Project in Python
-----------------------------------
This file is a complete, runnable CLI ATM app. It's organized step-by-step
so you can follow the logic from authentication through transactions.

Run it with:
    python atm_machine.py

The app stores data in accounts.json (created automatically on first run).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime
import json
import os
import getpass

# STEP 1 – Data Model & Persistence
# ------------------------------------------------------------
# We keep accounts in a JSON file so your balances persist
# between runs. The structure is:
# {
#   "12345": {"pin": "1111", "balance": 5000.0, "history": [...]},
#   "67890": {"pin": "2222", "balance": 3000.0, "history": [...]}
# }
DATA_FILE = "accounts.json"

@dataclass
class Account:
    pin: str
    balance: float = 0.0
    history: List[Dict] = field(default_factory=list)

    def record(self, type_: str, amount: float = 0.0, note: str = "") -> None:
        self.history.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "type": type_,
            "amount": round(float(amount), 2),
            "balance": round(float(self.balance), 2),
            "note": note,
        })


Accounts = Dict[str, Account]


def load_accounts(path: str = DATA_FILE) -> Accounts:
    if not os.path.exists(path):
        # First run: create a couple of demo accounts
        demo = {
            "12345": Account(pin="1111", balance=5000.0),
            "67890": Account(pin="2222", balance=3000.0),
        }
        save_accounts(demo, path)
        return demo

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    # Convert raw dicts to Account objects
    accounts: Accounts = {}
    for acc_no, info in raw.items():
        accounts[acc_no] = Account(
            pin=info["pin"],
            balance=float(info.get("balance", 0.0)),
            history=list(info.get("history", [])),
        )
    return accounts


def save_accounts(accounts: Accounts, path: str = DATA_FILE) -> None:
    serializable = {
        acc_no: {
            "pin": acc.pin,
            "balance": round(float(acc.balance), 2),
            "history": acc.history,
        }
        for acc_no, acc in accounts.items()
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(serializable, f, indent=2)


# ============================================================
# STEP 2 – Authentication
# ------------------------------------------------------------
# Ask for account number & PIN (hidden input). Allow 3 tries.
# ============================================================

def authenticate(accounts: Accounts) -> str | None:
    MAX_TRIES = 3
    for attempt in range(1, MAX_TRIES + 1):
        acc_no = input("\nEnter account number: ").strip()
        pin = getpass.getpass("Enter PIN: ").strip()
        account = accounts.get(acc_no)
        if account and pin == account.pin:
            print("\n✅ Login successful.")
            return acc_no
        else:
            left = MAX_TRIES - attempt
            print(f"❌ Invalid credentials. Tries left: {left}")
            if left == 0:
                print("\nYour card is blocked for this session. Exiting…")
                return None


# ============================================================
# STEP 3 – Utility Input Validators
# ------------------------------------------------------------
# Ensure we only accept valid positive numbers for money.
# ============================================================

def input_amount(prompt: str) -> float:
    while True:
        raw = input(prompt).strip()
        try:
            amount = float(raw)
            if amount <= 0:
                raise ValueError
            # Optional ATM-like constraint: multiples of 10
            if amount * 100 % 100 != 0:
                # Allow cents; comment the next 3 lines to force whole dollars
                return round(amount, 2)
            return round(amount, 2)
        except ValueError:
            print("Please enter a valid amount (e.g., 50 or 50.00).")


# ============================================================
# STEP 4 – Core Operations
# ------------------------------------------------------------
# Balance, Deposit, Withdraw, Transfer, History
# Each operation records a transaction.
# ============================================================

def check_balance(account: Account) -> None:
    print(f"\n💰 Current balance: ${account.balance:,.2f}")


def deposit(account: Account, amount: float) -> None:
    account.balance += amount
    account.record("DEPOSIT", amount, note="Cash deposit")
    print(f"\n✅ Deposited ${amount:,.2f}. New balance: ${account.balance:,.2f}")


def withdraw(account: Account, amount: float) -> None:
    if amount > account.balance:
        print("\n⚠️ Insufficient funds.")
        return
    account.balance -= amount
    account.record("WITHDRAW", amount, note="Cash withdraw")
    print(f"\n✅ Withdrawn ${amount:,.2f}. New balance: ${account.balance:,.2f}")


def transfer(accounts: Accounts, from_acc_no: str, to_acc_no: str, amount: float) -> None:
    if from_acc_no == to_acc_no:
        print("\n⚠️ Cannot transfer to the same account.")
        return
    to_account = accounts.get(to_acc_no)
    if not to_account:
        print("\n⚠️ Target account does not exist.")
        return
    from_account = accounts[from_acc_no]
    if amount > from_account.balance:
        print("\n⚠️ Insufficient funds.")
        return

    # Deduct from sender, add to receiver
    from_account.balance -= amount
    to_account.balance += amount

    from_account.record("TRANSFER_OUT", amount, note=f"To {to_acc_no}")
    to_account.record("TRANSFER_IN", amount, note=f"From {from_acc_no}")
    print(
        f"\n✅ Transferred ${amount:,.2f} to {to_acc_no}. New balance: ${from_account.balance:,.2f}"
    )


def show_history(account: Account, limit: int = 10) -> None:
    if not account.history:
        print("\n(No transactions yet.)")
        return
    print("\n📜 Last transactions:")
    for item in account.history[-limit:]:
        print(
            f"  {item['time']}  |  {item['type']:13}  |  ${item['amount']:>8,.2f}  |  Bal: ${item['balance']:>8,.2f}  |  {item['note']}"
        )


# ============================================================
# STEP 5 – Menus & App Loop
# ------------------------------------------------------------
# A simple text UI that calls the operations above and
# persists data after each change.
# ============================================================

def main_menu() -> str:
    print(
        """
==============================
        ATM MAIN MENU
==============================
1) Check Balance
2) Deposit
3) Withdraw
4) Transfer
5) Transaction History
6) Exit
"""
    )
    return input("Choose an option (1-6): ").strip()


def run_app() -> None:
    accounts = load_accounts()
    print("\n👋 Welcome to the Python ATM")

    acc_no = authenticate(accounts)
    if not acc_no:
        return

    while True:
        choice = main_menu()
        account = accounts[acc_no]

        if choice == "1":
            check_balance(account)

        elif choice == "2":
            amt = input_amount("Enter deposit amount: $")
            deposit(account, amt)
            save_accounts(accounts)

        elif choice == "3":
            amt = input_amount("Enter withdrawal amount: $")
            withdraw(account, amt)
            save_accounts(accounts)

        elif choice == "4":
            target = input("Enter target account number: ").strip()
            amt = input_amount("Enter transfer amount: $")
            transfer(accounts, acc_no, target, amt)
            save_accounts(accounts)

        elif choice == "5":
            show_history(account, limit=10)

        elif choice == "6":
            print("\n👋 Thank you for banking with us. Goodbye!")
            save_accounts(accounts)
            break

        else:
            print("\nPlease choose a valid option (1-6).")


if __name__ == "__main__":
    run_app()
