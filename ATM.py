import tkinter as tk
from tkinter import messagebox
import csv
import os

# Define the User class
class User:
    def __init__(self, name, pwd, card_number, pin, initial_balance=0):
        self.name = name
        self.pwd = pwd
        self.card_number = card_number
        self.pin = pin
        self.balance = initial_balance
        self.transaction_history = []
    
    def checkPassword(self, pwd):
        return self.pwd == pwd
    
    def checkPin(self, entered_pin):
        return self.pin == entered_pin
    
    def updateBalance(self, amount):
        self.balance += amount
        return self.balance
    
    def getBalance(self):
        return self.balance
    
    def addTransaction(self, transaction):
        self.transaction_history.append(transaction)

    def getTransactionHistory(self):
        return self.transaction_history

# Define the Login class
class Login:
    def __init__(self, csv_file='accounts.csv'):
        self.accounts = {}
        self.csv_file = csv_file
        self.loadAccounts()

    def loadAccounts(self):
        if os.path.exists(self.csv_file):
            with open(self.csv_file, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    name, pwd, card_number, pin, balance, history = row
                    user = User(name, pwd, card_number, pin, float(balance))
                    user.transaction_history = history.split("|")
                    self.accounts[name] = user

    def addAccount(self, userName, password, card_number, pin, balance=0):
        if userName in self.accounts:
            print("Account already exists.")
        else:
            new_user = User(userName, password, card_number, pin, balance)
            self.accounts[userName] = new_user
            self.saveToCSV(new_user)
            print(f"Account created successfully for {userName} with initial balance of {balance}.")

    def saveToCSV(self, user):
        with open(self.csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user.name, user.pwd, user.card_number, user.pin, user.balance, "|".join(user.transaction_history)])

    def login(self, card_number, pin):
        for user in self.accounts.values():
            if user.card_number == card_number and user.checkPin(pin):
                return user
        return None

# Define the Bank class
class Bank:
    def __init__(self, login_system):
        self.login_system = login_system

    def getBalance(self, card_number, pin):
        user = self.login_system.getUserByCard(card_number, pin)
        if user:
            return user.getBalance()
        return None

# GUI using Tkinter
class ATM_GUI:
    def __init__(self, root, login_system):
        self.root = root
        self.login_system = login_system
        self.current_user = None
        
        self.root.title("ATM System")
        self.root.geometry("400x300")
        
        self.create_login_screen()

    def create_login_screen(self):
        self.clear_screen()
        
        # Create login screen UI
        tk.Label(self.root, text="Enter Card Number").pack(pady=10)
        self.card_number_entry = tk.Entry(self.root)
        self.card_number_entry.pack(pady=5)
        
        tk.Label(self.root, text="Enter PIN").pack(pady=10)
        self.pin_entry = tk.Entry(self.root, show="*")
        self.pin_entry.pack(pady=5)
        
        tk.Button(self.root, text="Login", command=self.login_user).pack(pady=20)

    def login_user(self):
        card_number = self.card_number_entry.get()
        pin = self.pin_entry.get()

        if card_number and pin:
            user = self.login_system.login(card_number, pin)
            if user:
                self.current_user = user
                messagebox.showinfo("Success", f"Welcome {user.name}!")
                self.create_main_menu()
            else:
                messagebox.showerror("Error", "Invalid card number or PIN")
        else:
            messagebox.showwarning("Input Error", "Please enter both card number and PIN")

    def create_main_menu(self):
        self.clear_screen()

        # Main Menu UI
        tk.Label(self.root, text="ATM Main Menu").pack(pady=10)
        
        tk.Button(self.root, text="Deposit", command=self.deposit_screen).pack(pady=5)
        tk.Button(self.root, text="Withdraw", command=self.withdraw_screen).pack(pady=5)
        tk.Button(self.root, text="Check Balance", command=self.check_balance).pack(pady=5)
        tk.Button(self.root, text="Transaction History", command=self.transaction_history).pack(pady=5)
        tk.Button(self.root, text="Logout", command=self.create_login_screen).pack(pady=20)

    def deposit_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter amount to deposit").pack(pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=5)

        tk.Button(self.root, text="Deposit", command=self.deposit).pack(pady=10)

    def deposit(self):
        amount = self.amount_entry.get()
        if amount.isdigit():
            amount = float(amount)
            self.current_user.updateBalance(amount)
            self.current_user.addTransaction(f"Deposited: {amount}")
            messagebox.showinfo("Success", f"Deposited {amount}. New balance: {self.current_user.getBalance()}")
        else:
            messagebox.showerror("Error", "Invalid amount")

        self.create_main_menu()

    def withdraw_screen(self):
        self.clear_screen()

        tk.Label(self.root, text="Enter amount to withdraw").pack(pady=10)
        self.amount_entry = tk.Entry(self.root)
        self.amount_entry.pack(pady=5)

        tk.Button(self.root, text="Withdraw", command=self.withdraw).pack(pady=10)

    def withdraw(self):
        amount = self.amount_entry.get()
        if amount.isdigit():
            amount = float(amount)
            if self.current_user.getBalance() >= amount:
                self.current_user.updateBalance(-amount)
                self.current_user.addTransaction(f"Withdrew: {amount}")
                messagebox.showinfo("Success", f"Withdrew {amount}. New balance: {self.current_user.getBalance()}")
            else:
                messagebox.showerror("Error", "Insufficient balance")
        else:
            messagebox.showerror("Error", "Invalid amount")

        self.create_main_menu()

    def check_balance(self):
        messagebox.showinfo("Balance", f"Your balance is: {self.current_user.getBalance()}")

    def transaction_history(self):
        history = "\n".join(self.current_user.getTransactionHistory())
        messagebox.showinfo("Transaction History", f"Your transaction history:\n{history}")

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# Main function to start the ATM
def main():
    login_system = Login()

    root = tk.Tk()
    atm_gui = ATM_GUI(root, login_system)

    root.mainloop()

if __name__ == "__main__":
    main()
