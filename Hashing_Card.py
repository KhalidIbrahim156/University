import shelve
import random
import hashlib
import tkinter as tk
from tkinter import messagebox
from datetime import date


# Include your existing functions here (unchanged)

def generate_charge_value(amount, block):
    tempV = str(amount)
    val = ord(tempV[0]) - 48
    generatedCode = "xxxxxxxxxxxxxxxx"
    gcl = list(generatedCode)  # Generated code as list
    rpos = random.randint(len(tempV), 12)
    gcl[rpos] = str(val)

    j = 1
    if len(tempV) >= 1:
        for i in range(rpos - 1, rpos - len(tempV), -1):
            gcl[i] = tempV[j]
            if tempV[j] not in block:
                block.append(tempV[j])
            j += 1
    generatedCode = ''.join(gcl)
    return generatedCode, block


def generate_date(amount, block):
    code, block = generate_charge_value(amount, block)
    gcl = list(code)  # Generated code as list

    current_date = str(date.today())
    today = (ord(current_date[5]) - 48) * 10 + (ord(current_date[6]) - 48)

    pos = 0
    for i in range(14):
        if code[i] != 'x':
            pos = i
    gcl[pos + 1] = str(today % 10)
    if today % 10 not in block:
        block.append(str(today % 10))
    today //= 10
    gcl[pos + 2] = str(today)
    if today not in block:
        block.append(str(today))
    code = ''.join(gcl)
    return code, block


def Luhn_algorithm(num, f):
    if f == 0:
        digits = [int(d) for d in num]
    else:
        digits = list()
        for d in range(len(num) - 1):
            digits.append(int(num[d]))

    for i in range(len(digits) - 1, -1, -2):
        digits[i] *= 2
        if digits[i] > 9:
            digits[i] -= 9

    totalSum = sum(digits)
    return str((10 - (totalSum % 10)) % 10)


def generate_card_number(charge_value, block):
    code, block = generate_date(charge_value, block)
    tempL = list(code)
    for i in range(len(tempL)):
        if tempL[i] == 'x' and i != len(tempL) - 1:
            d = str(random.randint(0, 9))
            while d in block:
                d = str(random.randint(0, 9))
            tempL[i] = d
    gNum = ''.join(tempL)
    lastDigit = Luhn_algorithm(gNum, 1)
    tempL[15] = lastDigit
    gNum = ''.join(tempL)
    return gNum, block


def Charge_value(block):
    current_date = date.today()
    current_date = str(current_date)
    ans = 0
    if len(block) == 2:
        return '20 LE has been added to your card.'
    else:
        if block[1] == '0':
            return '100 LE has been added to your card.'
        ans = ord(block[0]) - 48
        ans *= 10
        for i in range(1, len(block) - 2):
            ans += (ord(block[i]) - 48)
            ans *= 10
        return f'{ans} LE has been added to your card.'


def Validate(card_number):
    check = card_number[-1]
    body = card_number[:-1]
    return Luhn_algorithm(body, 0) == check


def brute_force_attack(card_number, block):
    if len(set(card_number)) < 5:
        return False
    d = dict()
    for i in range(0, 15):
        if card_number[i] in d:
            d[card_number[i]] += 1
        else:
            d[i] = 1
    for val in block:
        if d.get(val, 0) > 2:
            return False
    return True


def predict_Validate(card_number, block):
    return brute_force_attack(card_number, block) == Validate(card_number) == 1


def generate_card_info(card_number):
    current_date = date.today()
    current_date = str(current_date)

    block = list()

    pos = 0
    for i in range(0, 14):
        if card_number[i] == current_date[6] and card_number[i + 1] == current_date[5]:
            pos = i
            break

    if card_number[pos - 1] not in block:
        block.append(card_number[pos - 1])
    if card_number[pos - 1] == '1' and pos - 2 >= 0:
        if card_number[pos - 2] == '0':
            if card_number[pos - 2] not in block:
                block.append(card_number[pos - 2])
    if current_date[5] not in block:
        block.append(current_date[5])
    if current_date[6] not in block:
        block.append(current_date[6])
    return block


def expire_date(card_number):
    current_date = date.today()
    current_date = str(current_date)
    month = current_date[5:7]
    month = month[1] + month[0]
    if month not in card_number:
        return False
    return True


# GUI Implementation

def generate_card_gui():
    try:
        charge_value = str(charge_value_entry.get())
        block = [charge_value[0]]
        if charge_value[1] != '0':
            block.append(charge_value[1])
        card_number, block = generate_card_number(str(charge_value), block)

        # Check for duplicates
        with shelve.open("Hashing_card") as db:
            while card_number in db:
                card_number, block = generate_card_number(str(charge_value), block)

        result_label.config(text=f"Generated Card: {card_number}")
    except ValueError:
        messagebox.showerror("Invalid Input", "Please enter a valid number.")


def charge_card_gui():
    card_number = card_number_entry.get()
    with shelve.open("Hashing_card") as db:
        if card_number in db:
            messagebox.showerror("Error", f"The card {card_number} has already been used.")
        else:
            if expire_date(card_number):
                block = generate_card_info(card_number)
                if predict_Validate(card_number, block):
                    db[card_number] = True
                    charge_message = Charge_value(block)
                    db[card_number] = True
                    messagebox.showinfo("Success", charge_message)
                else:
                    messagebox.showerror("Invalid Card", "Invalid card number.")
            else:
                messagebox.showerror("Expired Card", "The card has expired.")


# Main GUI
root = tk.Tk()
root.title("Card Generator and Charger")
root.geometry("400x400")

# Input fields and buttons
charge_value_label = tk.Label(root, text="Enter charge value (e.g., 10, 25, 50, 100):")
charge_value_label.pack(pady=5)

charge_value_entry = tk.Entry(root)
charge_value_entry.pack(pady=5)

generate_button = tk.Button(root, text="Generate Card", command=generate_card_gui)
generate_button.pack(pady=10)

result_label = tk.Label(root, text="Generated Card: ")
result_label.pack(pady=5)

card_number_label = tk.Label(root, text="Enter card number to charge:")
card_number_label.pack(pady=5)

card_number_entry = tk.Entry(root)
card_number_entry.pack(pady=5)

charge_button = tk.Button(root, text="Charge Card", command=charge_card_gui)
charge_button.pack(pady=10)

exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=20)

root.mainloop()

