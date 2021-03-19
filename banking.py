import sqlite3
from random import randint

conn = sqlite3.connect("card.s3db")
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS card(id INTEGER primary key, number TEXT, pin TEXT, balance INTEGER default 0)")
conn.commit()


def luhn_checker(num):
    first = num[:-1]
    calc = []
    for i, n in enumerate(first):
        if i % 2 == 0:
            n = str(int(n) * 2)
        if int(n) > 9:
            n = str(int(n) - 9)
        calc.append(n)
    sum = 0
    calc.append(num[-1])
    for i in calc:
        sum += int(i)
    if (sum % 10 == 0):
        return True
    return False


def card_generator():
    num = "400000"
    for _ in range(9):
        num += str(randint(0, 9))
    checksum = 0
    for i, n in enumerate(num):
        if i % 2 == 0:
            n = str(int(n) * 2)
        if int(n) > 9:
            n = str(int(n) - 9)
        checksum += int(n)
    if checksum % 10 == 0:
        num += "0"
    else:
        num += str(10 - checksum % 10)
    pin = str(randint(1000, 9999))
    if not cur.execute("SELECT number FROM card WHERE number = ?", (str(num),)).fetchall():

        print("Your card number:")
        print(num)
        print("Your card PIN:")
        print(pin)
        cur.execute("insert into card(number ,pin) values (?,?)", (num, pin))
        conn.commit()
    else:
        card_generator()


def update_balance(amt, cardnum):
    cur.execute("UPDATE card SET balance = (?)  WHERE number = (?)", (amt, cardnum))
    conn.commit()
    cur.execute("SELECT * FROM card WHERE number = (?)", (cardnum,))


while True:
    print("1. Create an account")
    print("2. Log into account")
    print("0. Exit")
    choice = int(input())
    if choice == 0:
        print("Bye!")
        conn.commit()
        conn.close()
        exit()
    elif choice == 1:
        card_generator()
        conn.commit()
    else:
        print("Enter your card number:")
        c = input()
        print("Enter your PIN:")
        p = input()
        query = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?", (str(c),)).fetchall()
        if query != [] and query[0][1] == p:
            print("You have successfully logged in!")
            while True:
                print("1. Balance")
                print("2. Add income")
                print("3. Do transfer")
                print("4. Close account")
                print("5. Log out")
                print("0. Exit")
                choice2 = int(input())
                if choice2 == 0:
                    print("Bye!")
                    conn.commit()
                    conn.close()
                    exit()
                elif choice2 == 1:
                    print("Balance:", query[0][2])
                elif choice2 == 2:
                    print("Enter income:")
                    amt = cur.execute("SELECT  balance FROM card WHERE number = ?",
                                      (c,)).fetchone()[0]
                    amt = int(input()) + amt
                    update_balance(amt, query[0][0])
                    conn.commit()
                    print("Income was added!")
                elif choice2 == 3:
                    print("Transfer")
                    print("Enter card number:")
                    card_num = input()
                    if luhn_checker(card_num):
                        quer = cur.execute("SELECT number, pin, balance FROM card WHERE number = ?",
                                           (card_num,)).fetchall()
                        if quer:
                            if card_num == c:
                                print("You can't transfer money to the same account!")
                            else:
                                print("Enter how much money you want to transfer:")
                                trans = int(input())
                                if trans > cur.execute("SELECT  balance FROM card WHERE number = ?",
                                                       (c,)).fetchone()[0]:
                                    print("Not enough money!")
                                else:
                                    amt = cur.execute("SELECT  balance FROM card WHERE number = ?",
                                                      (c,)).fetchone()[0]
                                    amt2 = cur.execute("SELECT  balance FROM card WHERE number = ?",
                                                       (card_num,)).fetchone()[0]
                                    amt = amt - trans
                                    amt2 = amt2 + trans
                                    update_balance(amt, card_num)
                                    update_balance(amt2, c)
                                    print("Success!")
                        else:
                            print("Such a card does not exist.")
                    else:
                        print("Probably you made a mistake in the card number. Please try again!")
                elif choice2 == 4:
                    cur.execute("DELETE FROM card where number = ?", (c,))
                    conn.commit()
                    print("The account has been closed!")
                    break
                else:
                    print("You have successfully logged out!")
                    break

        else:
            print("Wrong card number or PIN!")
