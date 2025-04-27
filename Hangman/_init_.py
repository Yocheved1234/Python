import sys
from flask import Flask, request, jsonify, make_response, abort
from user import User
from logo_homon import Homon, logoL
from requests import session
from Server import all_user, find_word
from colorama import Fore, Back, Style
from tqdm import tqdm
from datetime import datetime
import time

app = Flask(__name__)
session = session()
basic_url = "http://127.0.0.1:5000"
homon = Homon

# הבאת הלוגו והכנתו להדפסה
def logo():
    logo=logoL
    print(Fore.BLUE + logo)
# בדיקת תקינות על המספר שהשחקן מכניס לבחירת מילה
def valid_number():
    # פעולה זו נעשת עד שהלקוח לא מכניס משהו תקין
    while True:
        try:
            return int(input(Fore.CYAN+"input num word: "))  # מחזיר את המספר אם הוא תקין
        except ValueError:
            print("Please enter a valid number.") # מחזיר לו שהארך של המספר לא תקין
# אחרי שלשחקן נגמר הקוקיז, כאן אני שואלת אם הוא רוצה להתחבר שוב.
def play_again():
    # אני לר משחררת לו כל זמן שהוא לא מחזיר לי תשובה תקינה
    while True:
        qu = input("Do you want to join again? (yes/no) ").lower()
        if qu == 'yes':
            login() # אם כן אני שולחת אישור אני מתחילה את המשחק שוב
            return
        elif qu == 'no': # אם אני שולחת לא הוא יוצא
            return 'no'
        else: # אם אני שולחת קלט לא תקין הוא מחזיר לי בקשה לשלוח שוב, והפעם תקין
            print("The input you provided is not valid. Please enter 'yes' or 'no'.")
# המשחק בעצמו, מקבל שם וקוד של השחקן
def game(name, password):
    num = valid_number() # מבקש שיכניס מספר להגרלת מילה, ובודק שהוא יהיה תקין
    the_w = find_word(num)# מפעיל פונקציה מהשרת ומחזיר את המילה ע"פ בקשת השחקן
    the_l = ['*' if c != ' ' else ' ' for c in the_w] # עוברת על המילה ובמקום אות מכניסה כוכבית
    print(''.join(the_l)) # הדפסת המילה באותיות
    # שמירת הפרטים בJASON כדי לשלוח את זה לשרת במקרא של נצחון
    data = {'name': name, 'password': password, 'word': the_w}
    h = 0 # שמירת משתנה להדפסת העץ במקרא של כשלון
    letters_set = set() # מארך לשמירת כל האותיות שכבר הוכנסו
    while h < len(homon) and ''.join(the_l) != the_w: #הלולאה תפעל כל זמן שהעץ לא בנוי והמילה לא שווה למילה עם הכוכביות
        letur = input(Fore.RESET + "input letur: ") # הכנסת אות
        while True: # כל זמן שהוא לא מכניס לי אות שלא חזר על עצמו
            if letur.lower() in letters_set: # אם האות כבר נמצאת מבקש אות נוספת
                print("The letter is already selected.")
                letur = input(Fore.RESET + "input letur: ")

            else:
                letters_set.add(letur.lower()) # אם לא קיימת, מוסיף למערך של הSET
                break
        if letur.isalpha() and len(letur) == 1 and letur.isascii(): # אם הוא אות וגם האורך לא גדול מ1 וגם באנגלית
            if letur.lower() in the_w.lower(): # בודק האם האות קיימת במילה
                the_l = [letur.upper() if c == letur.upper() else letur.lower() if c == letur.lower() else l for c, l
                         in zip(the_w, the_l)] # אם הוא קיים הוא משנה במיקום להיות עם אות ולא כוכבית
                print(''.join(the_l))
            else:
                print(homon[h]) # מדפיס חלק מהעץ
                h += 1 # מקדם את האינדקס
        elif letur.isdigit(): # אם הוכנס מספר מחזיר בקשה נוספת להכנסת אות תקינה
             print("Invalid input: The input must not be a number.")
        elif not letur.isalpha(): # אם הוכנס לא אות מחזיר בקשה נוספת להכנסת אות תקינה
             print("Invalid input: The input must contain only letters.")
        elif len(letur) != 1: # אם הוכנס יותר מאות אחת מחזיר בקשה נוספת להכנסת אות תקינה
              print("Invalid input: The input must be exactly one character long.")
        elif not letur.isascii(): # אם הוכנס אות בעברית מחזיר בקשה נוספת להכנסת אות תקינה
              print("Invalid input: The input must be an English letter.")

    if ''.join(the_l) == the_w: # בודק אם סיבת היציאה הוא בגלל הצלחה
            if session.post(f'{basic_url}/add_win', json=data).status_code == 401: # אם הוספת מילה למארך מחזיר שגיעה מהדקורטור
                 print("Your number was not put in.....") # מעדכן אל בעיה בהוספת המילה
                 r = play_again() # מציאה למשתמש להרשם שוב
                 if r=='no': # אם התשובה היא לא
                     sys.exit() # הוא יוצא
            else: # אם הוא הצליח להוסיף את המילה וגם הקוקיז עדיין פועל
                print(Fore.RED+"Saving info.....")
                for i in tqdm(range(20)):
                    time.sleep(0.1)
                print(Fore.CYAN+"you win😉😊🥰!!!!!!!!!!!") # מעדכן על נצחון
                after(name, password) # שולחת לפונקציה להציאה לו הצאות...
                sys.exit()
    elif h == len(homon): # אם יצא בגלל הכשלון
        print(Fore.RED + "Saving info.....")
        for i in tqdm(range(20)):
             time.sleep(0.1)
        print(the_w)
        print(Fore.RED + "You lost! Better luck next time.") # מעדכן על הכשלון
        sys.exit() # יוצא
# הצאת הצאות לאחר נצחון
def after(name, password):
    while True: # לא משחרר כל זמן שאין קלט טוב
        try:
            qwestchen = int(input("""Choose one of the following options:
            If you want to continue playing press 1,
            If you want to see your game history - press 2,
            To exit press 3  """))

            if qwestchen == 1: # אם הוא בוחר אחד, הפעלת משחק חדש
                game(name, password)
                break
            elif qwestchen == 2: # אם הוא בוחר שתיים הדפסת כל המילים שהצליח
                print([i['words'] for i in all_user() if i['name'] == name and i['password'] == password])
                break
            elif qwestchen == 3: # אם שלוש, יציאה
                print("Exiting the game.")
                break
            else:
                print("Please enter a valid option: 1, 2, or 3.") #אם זה מספר ולא אחד טוב, ובקש מספר בין 1-3

        except ValueError as er: # אם זה לא מספר זורק את השגיעה ומבקש מספר
            print(f"Error! Invalid input: {er}. Please enter a number.")
        except Exception as e: # לכל שגיעה אחרת, זורק אותה
            print(f"An unexpected error occurred: {e}")
# כניסה למשחק
def login():
    current_time = datetime.now() # הדפסת הזמן הנוכחי
    print("Current time:", current_time)

    while True: # לא משחרר, כל זמן שלא הוכנס שם טוב
        try:
            name = input(Fore.GREEN+"Enter your name: ") # דורש רק אותיות
            if not name.isalpha():
                raise ValueError("Error: Name must contain only letters. Please enter a valid name.")

            password = input("Enter your password: ") # מקבל קוד

            data = {'name': name, 'password': password} # מיצר JSON של שם וקוד
            print(Fore.RED+session.post(f'{basic_url}/login', json=data).text) # מפעיל את פונקצית כניסה מהשרת
            game(name, password) # שולח לפונקצית משחק
            break

        except ValueError as e: # אם יש שגיעה בשם מחזיר לי אתה
            print(e)
        except Exception as e: # אם יש כל שגיעה אחרת מחזיר לי אותה
            print(f"Unexpected error: {e}")


if __name__ == '__main__':
    logo() # הפעלת הלוגו
    login() # הפעלת הכניסה למשחק

print("_main_")
