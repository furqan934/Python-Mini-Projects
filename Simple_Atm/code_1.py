# simple atm with  signup and login then withdraw and deposit and show balance and histry 
# the account no will be issued to the users randomly 
from __future__ import  annotations
from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime
import random
import sys
import getpass
import json
import os
import re

#  we create a json data class for user
Data_File = "accounts.json"

@dataclass
class Account:
    account_no: str
    name: str
    password: str
    balance: float = 0.0
    history: List[Dict] = field(default_factory=list)

    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.balance += amount
        self.history.append({
            "type": "deposit",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
        self.balance -= amount
        self.history.append({
            "type": "withdraw",
            "amount": amount,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        def transfer(self, target_account: Account, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Transfer amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds for transfer.")
        if self.account_no == target_account.account_no:
            raise ValueError("Cannot transfer to the same account.")
        self.balance -= amount
        target_account.balance += amount
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append({
            "type": "transfer_out",
            "amount": amount,
            "to": target_account.account_no,
            "date": now
        })
        target_account.history.append({
            "type": "transfer_in",
            "amount": amount,
            "from": self.account_no,
            "date": now
        })    

    def get_balance(self) -> float:
        return self.balance

    def get_history(self) -> List[Dict]:
        return self.history

    def to_dict(self) -> Dict:
        return {
            "account_no": self.account_no,
            "name": self.name,
            "password": self.password,
            "balance": self.balance,
            "history": self.history
        }

    @staticmethod
    def from_dict(data: Dict) -> Account:
        return Account(
            account_no=data["account_no"],
            name=data["name"],
            password=data["password"],
            balance=data.get("balance", 0.0),
            history=data.get("history", [])
        )
    
class ATM:
    def __init__(self, data_file: str = Data_File):
        self.data_file = data_file
        self.accounts: Dict[str, Account] = self.load_accounts()
        self.current_account: Account | None = None

    def load_accounts(self) -> Dict[str, Account]:
        if not os.path.exists(self.data_file):
            return {}
        with open(self.data_file, 'r') as file:
            data = json.load(file)
            return {acc_no: Account.from_dict(acc_data) for acc_no, acc_data in data.items()}

    def save_accounts(self) -> None:
        with open(self.data_file, 'w') as file:
            data = {acc_no: acc.to_dict() for acc_no, acc in self.accounts.items()}
            json.dump(data, file, indent=4)

    def generate_account_no(self) -> str:
        while True:
            account_no = str(random.randint(10000000, 99999999))
            if account_no not in self.accounts:
                return account_no

    def signup(self) -> None:
        name = input("Enter your name: ")
        while True:
            password = getpass.getpass("Create a password (min 6 chars, include letters and numbers): ")
            if len(password) < 6 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
                print("Password must be at least 6 characters long and include both letters and numbers.")
            else:
                break
        account_no = self.generate_account_no()
        new_account = Account(account_no=account_no, name=name, password=password)
        self.accounts[account_no] = new_account
        self.save_accounts()
        print(f"Account created successfully! Your account number is {account_no}")

    def login(self) -> None:
        account_no = input("Enter your account number: ")
        password = getpass.getpass("Enter your password: ")
        account = self.accounts.get(account_no)
        if account and account.password == password:
            self.current_account = account
            print(f"Welcome back, {account.name}!")
        else:
            print("Invalid account number or password.")
            self.current_account = None
            return
        self.account_menu()
    def account_menu(self) -> None:
        while self.current_account:
            print("\n1. Deposit")
            print("2. Withdraw")
            print("3. Show Balance")
            print("4. Show History")
            print("5. Logout")
            choice = input("Choose an option: ")
            if choice == '1':
                amount = float(input("Enter amount to deposit: "))
                try:
                    self.current_account.deposit(amount)
                    self.save_accounts()
                    print(f"Deposited ${amount:.2f}. New balance: ${self.current_account.get_balance():.2f}")
                except ValueError as e:
                    print(e)
            elif choice == '2':
                amount = float(input("Enter amount to withdraw: "))
                try:
                    self.current_account.withdraw(amount)
                    self.save_accounts()
                    print(f"Withdrew ${amount:.2f}. New balance: ${self.current_account.get_balance():.2f}")
                except ValueError as e:
                    print(e)
            elif choice == '3':
                print(f"Current balance: ${self.current_account.get_balance():.2f}")
            elif choice == '4':
                history = self.current_account.get_history()
                if not history:
                    print("No transaction history.")
                else:
                    for record in history:
                        print(f"{record['date']}: {record['type'].capitalize()} of ${record['amount']:.2f}")
            elif choice == '5':
                print(f"Goodbye, {self.current_account.name}!")
                self.current_account = None
            else:
                print("Invalid option. Please try again.")
    def main_menu(self) -> None:
        while True:
            print("\n1. Signup")
            print("2. Login")
            print("3. Exit")
            choice = input("Choose an option: ")
            if choice == '1':
                self.signup()
            elif choice == '2':
                self.login()
            elif choice == '3':
                print("Thank you for using the ATM. Goodbye!")
                sys.exit()
            else:
                print("Invalid option. Please try again.")
if __name__ == "__main__":
    atm = ATM()
    atm.main_menu()
    