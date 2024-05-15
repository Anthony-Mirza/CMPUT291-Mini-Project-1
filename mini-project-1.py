import sqlite3
import sys
from getpass import getpass
from datetime import date

connection = None
cursor = None
user_email = None
import datetime

def connect(path):
    # Function connection the python file with the database file using the path provided
    # as a command line argument.
    global connection, cursor, user_email
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA forteign_keys=ON; ')
    connection.commit()
    return


def login_verify(email: str, password: str) -> tuple:
    # Function that verify the acount information from user with database
    global connection, cursor, user_email
    cursor.execute("SELECT * FROM members WHERE (email = ? OR LOWER(email) = LOWER(?)) AND passwd = ?;", (email, email, password))
    result = cursor.fetchone()
    if result is None: # No member in the database with the email provided. Invalid login. 
        return (False, None)
    else:
        matched_email = result[0] # Take out the returned mail from tuple.
        return (True, matched_email)

def login() -> bool:
    # Function that is triggered when user decides to login
    global connection, cursor, user_email

    print("-----\nLogin\n-----")
    email = input("Enter your email: ")
    password = getpass("Enter your password: ")
    result = login_verify(email, password) # Catch the tuple returned by login function
    if_pass = result[0]
    matched_email = result[1]
    if if_pass:
        print("Login successful!")
        user_email = matched_email # Set the email to be global
        return True
    else:
        print("Invalid email or password. Please try again.")
        return False
    

def signup() -> bool:
    # Function for signing up a new user.
    global connection, cursor, user_email

    print("-------\nSign up\n-------")
    email = input("Enter your email: ").strip() 
    if not email: # If user types nothing.
        print("Input can not be empty.\n")
        return False

    
    cursor.execute("SELECT * FROM members WHERE email = ?;", (email,)) # Query checks if any current member has the same email.
    existing_user = cursor.fetchone()

    if existing_user:
        print("Email address already exists. Please choose another one.") # If email is already being used, it will return false
        return False
    
    else: # Continue with account creation
        password = getpass("Enter your password: ").strip()
        if not password:
            print("Input can not be empty.\n")
            return False
        name = input("Enter your name: ").strip()
        if not name:
            print("Input can not be empty.\n")
            return False
        byear = input("Enter your birth year: ").strip()
        if not byear:
            print("Input can not be empty.\n")
            return False
        faculty = input("Enter your faculty: ").strip()
        if not faculty:
            print("Input can not be empty.\n")
            return False

        # Add the member to the members table in the database.
        cursor.execute("INSERT INTO members (email, passwd, name, byear, faculty) VALUES (?, ?, ?, ?, ?);", (email, password, name, byear, faculty))
        connection.commit()
        user_email = email # set the email to be global and go to the main menu
        print("Sign up successful!\n")
        return True

def login_menu():
    # Function handles the logic of navigation within the login menu.
    global connection, cursor, user_email

    print("Welcome to the Management System!\nMenu:")
    while True:
        print("1. Login\n2. Sign up\n3. Exit")
        choice = input("Please type in your choice: ")

        if choice == "1":
            logged_in = login()
            if logged_in == True: # If succesful main_menu() will be executed in main.
                return

        elif choice == "2":
            signed_in = signup() # If succesful main_menu() will be executed in main.
            if signed_in == True:
                return
        elif choice == "3":
            print("Thank you for using the Management System!")
            exit()
        else:
            print("Invalid input. Please try again!")


def myProfile():
    # Function displays the user's profile information.

    global connection, cursor, user_email
    email = user_email
    cursor= connection.cursor()
    cursor.execute(''' 
              SELECT name, email, byear 
              FROM members
              WHERE email = ?
                ''', (email,))
    
    personal_info = cursor.fetchone() # Get a single row which is the user's personal info
  
    print(f"\nName: {personal_info[0]}")
    print(f"Email: {personal_info[1]}")
    print(f"Birth Year: {personal_info[2]}")
    
    # Get the number of books a user has borrowed and returned.
    cursor.execute('''
            SELECT COUNT(bid)
            FROM borrowings
            WHERE member = ? 
            AND end_date IS NOT NULL
              ''', (email,))
    prev_borrows = cursor.fetchone()[0] 
    print(f"Previous Borrow Count: {prev_borrows} ") 

    # Get the number of books a user has borrowed but has not yet returned.
    cursor.execute('''
            SELECT COUNT(bid)
            FROM borrowings
            WHERE member = ? 
            AND end_date IS NULL 
              ''', (email,))
    current_borrows = cursor.fetchone()[0] 
    print(f"Current Borrow Count: {current_borrows} ")


    # Get the number of books a user has borrowed and has not yet returned by the 20 day deadline.
    cursor.execute('''
            SELECT COUNT(bid)
            FROM borrowings
            WHERE member = ? 
            AND end_date IS NULL
            AND (CAST(JULIANDAY('now') AS INTEGER) - CAST(JULIANDAY(start_date) AS INTEGER)) > 20;
              ''', (email,))
    overdue_borrows = cursor.fetchone()[0] 
    print(f"Overdue Borrow Count: {overdue_borrows} ")

    # Get the number of penalties the user has not paid in full yet. 
    cursor.execute('''
            SELECT COUNT(pid)
            FROM borrowings
            LEFT JOIN penalties ON
            borrowings.bid = penalties.bid
            WHERE member = ? 
            AND amount > IFNULL(paid_amount, 0)
              ''', (email,))
    num_unpaid_penalties = cursor.fetchone()[0] 
    print(f"Number of unpaid penalties: {num_unpaid_penalties} ")

    # Get the total amount of money the user still has to pay for penalties they were charged.
    cursor.execute('''
            SELECT IFNULL(SUM(amount), 0) - IFNULL(SUM(paid_amount), 0) AS amount_due
            FROM borrowings 
            LEFT JOIN penalties ON 
            borrowings.bid = penalties.bid
            WHERE member = ? 
            AND (amount > paid_amount
            OR paid_amount IS NULL)        
              ''', (email,))
    penalty_amount_due = cursor.fetchone()[0] 
    print(f"Penalty Amount Due: ${penalty_amount_due}\n ")


def payPenalty():
    # Function for paying a user's penalty
    global connection, cursor, user_email
    email = user_email
    cursor.execute('''
                SELECT pid, amount, IFNULL(paid_amount, 0)
                FROM borrowings 
                JOIN penalties ON 
                borrowings.bid = penalties.bid
                WHERE member = ?
                AND (amount > paid_amount OR paid_amount IS NULL) 
                ''', (email,))
    penalties_array = cursor.fetchall()
    num_of_penalties = len(penalties_array)

    if num_of_penalties == 0:
        print("You have no unpaid penalties!") # No penalties so go back to main menu.
        return
    
    else: # num_of_penalties > 0
        print()
        while True:
            cursor.execute('''
                SELECT pid, amount - IFNULL(paid_amount, 0), IFNULL(paid_amount, 0)
                FROM borrowings 
                JOIN penalties ON 
                borrowings.bid = penalties.bid
                WHERE member = ?
                AND (amount > paid_amount OR paid_amount IS NULL)
                ''', (email,))
            
            penalties_array = cursor.fetchall() # Rows of user's penalties
            num_of_penalties = len(penalties_array)
            
            if num_of_penalties == 0: # In case we initially had penalties, paid them, and are still in while loop.
                print("You have no unpaid penalties!")
                return
            
            for i in range(num_of_penalties): # i is used to iterate thru the array of tuples of user's penalties
                print(f"{i + 1}. Penalty ID: {penalties_array[i][0]} | Total Amount Due: ${penalties_array[i][1]} | Amount Paid: ${penalties_array[i][2]}")
            print('\nEnter 0 (zero) to go back to main menu.\nSelect a penalty to pay in full or partially: ')

            penalty_number = input("Penalty: ") 
            if penalty_number.isdigit() and int(penalty_number) >= 1 and int(penalty_number) <= num_of_penalties: # Checking that you selected a valid penalty
                penalty_number = int(penalty_number)
                amount_to_pay = input("Enter amount to pay: $").strip()
                if not amount_to_pay or not amount_to_pay.isdigit() or int(amount_to_pay) <= 0: # Input validation.
                    print("Invalid amount, please try again.")
                    continue
                penalty_pid = penalties_array[penalty_number-1][0] # Subtract 1 to get back to 0-based counting
                cursor.execute('''
                UPDATE penalties
                SET paid_amount = IFNULL(paid_amount, 0) + ?
                WHERE pid  = ?                            
                ''', (amount_to_pay, penalty_pid)) # Query updates the amount you've paid for this specific penalty.
                connection.commit() # Update the database with the changes made.
                print(f"Penalty {penalty_pid} paid, thanks!\n")
            
            elif penalty_number.isdigit() and int(penalty_number) == 0:
                break
            else:
                print("invalid penalty. Try again.\n")
    return

def search_books(keyword: str, page_num: int) -> list:
    # Searching for books to borrow
    global connection, cursor, user_email

    offset_num = page_num * 5 # Var keeps track of which page we're displaying via OFFSET clause in SQL
    search = """
            SELECT  b.book_id, b.title, b.author, b.pyear, AVG(r.rating) AS average_rating, 
            (CASE WHEN (bo.end_date IS NULL AND latest.latest_start_date IS NOT NULL) THEN 'Borrowed'
                ELSE 'Available'
            END) AS availability
            FROM books b
            LEFT JOIN (
            SELECT book_id, MAX(start_date) AS latest_start_date
            FROM borrowings
            GROUP BY book_id
            ) latest ON b.book_id = latest.book_id
            LEFT JOIN borrowings bo ON b.book_id = bo.book_id
            LEFT JOIN reviews r ON b.book_id = r.book_id
            WHERE LOWER(b.title) LIKE '%' || LOWER(?) || '%' OR LOWER(b.author) LIKE '%' || LOWER(?) || '%'
            GROUP BY b.book_id, b.title, b.author, b.pyear
            ORDER BY (
                CASE
                    WHEN LOWER(b.title) LIKE '%' || LOWER(?) || '%' THEN 1
                    ELSE 2
                END
            ) ASC
            LIMIT 5
            OFFSET ?;
    """
    cursor.execute(search, (keyword, keyword, keyword, offset_num))
    result = cursor.fetchall()
    return result 

def borrow_book(b_id: str):
    # Function for borrowing a book from the list
    global connection, cursor, user_email

    if not b_id.isdigit():
        print("Invalid book id. Please try again.")
        return

    cursor.execute("SELECT * FROM borrowings bo WHERE bo.book_id = ? AND end_date IS NULL;", (b_id,))
    existing_borrow = cursor.fetchall() # Check if this book is borrowed

    if len(existing_borrow) != 0: # Book is currently being borrowed!
        print("Sorry, the book is already borrowed.")
    else:
        start_date = date.today() # Start_date of borrow will be today's date
        cursor.execute("SELECT IFNULL(MAX(bid), 0) FROM borrowings")
        max_bid = cursor.fetchone()[0]
        new_bid = max_bid + 1 # Initialize a new bid, based on the current largest one in database
        cursor.execute("INSERT INTO borrowings (bid, member, book_id, start_date, end_date) VALUES (?, ?, ?, ?, ?)", (new_bid, user_email, b_id, start_date, None))
        connection.commit()
        print("Book has been borrowed successfully.")
    
    return

def search_menu():
    # Function for opening the search menu
    global connection, cursor, user_email

    print("------------\nSearch books\n------------")
    keyword = input("Please type in the keyword you want to search: ").strip()
    if not keyword:
        print("Keyword can not be empty.\n")
        return
    page_num = 0 # Used to track which page we want to display via OFFSET
    while True: # First while loop
        result = search_books(keyword, page_num)
        print(f"\nSearch result (page {page_num + 1}):")
        book_search_bid = []
        for i in result:
            book_search_bid.append(i[0]) # Append book ids
            print(f"Book id: {i[0]}, Title: {i[1]}, Author: {i[2]}, Year: {i[3]}, Average rating: {i[4]}, Availability: {i[5]}")
        while True: # Second while loop
            print("------------")
            choice = input("Press 1 to go to the next page, press 2 to borrow a book, press 3 to quit searching: ")
            if choice == "1": # If user types 1, we increment the page_num so that user could see the content for page 2
                page_num += 1
                break
            elif choice == "2": # If user types 2, we ask for the book id to be borrowed

                book_id = input("What is the id of the book you want to borrow? (press 0 to quit): ")

                while True: #input validation
                    if book_id.isdigit() == True:
                        if int(book_id) in book_search_bid or int(book_id) == 0:
                            break
                        else: book_id = input("Invalid input. What is the id of the book you want to borrow? (press 0 to quit): ")
                    else: book_id = input("Invalid input. What is the id of the book you want to borrow? (press 0 to quit): ")
                if int(book_id) == 0:
                    break
                borrow_book(book_id)
                break
            elif choice == "3": # Exit the searching
                print("Search ending...\n")
                return
            else:
                print("Invalid input, please try again.")
                break


def Borrowings():
    # Function for returning book menu that shows all of your current borrowings
    global connection, cursor, user_email

    user_borrowing = [] # contains bid of all user's current borrows
    cursor.execute('''
                SELECT b.bid, bk.title, b.start_date, IFNULL (b.end_date, DATE(b.start_date, '+20 days')) AS deadline
                FROM borrowings b
                LEFT JOIN members m ON b.member = m.email
                LEFT JOIN books bk ON b.book_id = bk.book_id
                WHERE b.member = ? 
                AND b.end_date IS NULL
                ''', (user_email,))

    rows = cursor.fetchall()   
 
    if len(rows) == 0: # In case you have zero borrowings
        print("You have no books to return.")
        return
    
    while True:
        cursor.execute('''
                SELECT b.bid, bk.title, b.start_date, IFNULL (b.end_date, date(b.start_date, '+20 days')) AS deadline
                FROM borrowings b
                LEFT JOIN members m ON b.member = m.email
                LEFT JOIN books bk ON b.book_id = bk.book_id
                WHERE b.member = ? 
                AND b.end_date IS NULL
                ''', (user_email,)) 
                # The reason for using the same query twice is to see the changes that were reflected in the db
                # Otherwise, changes will be made, but you will not see them being updated in real time
        
        rows = cursor.fetchall() 
        if len(rows) == 0: # In case you have zero borrowings
            print("You have no books to return.")
            return
        
        for row in rows:
            user_borrowing.append(row[0]) # append bid- we need it later in returnBook function
            print(f"Borrow ID: {row[0]} | Title: {row[1]} | Borrow Date: {row[2]} | Due Date: {row[3]}")

        print('''Enter\n1. Return book\n2. Back to main menu''')

        select = input('Enter 1 to return a book or 2 to return to the main menu: ') 

        if select == "1":
            returnBook(user_borrowing)
            user_borrowing.clear() # reset the user's borrowing bids
        elif select == "2":
            break # breaking out of current loop will return to main_menu()
        else:
            print("Invalid input. Please enter 1 or 2.")


def returnBook(user_borrowing):
    # Function handles returning a book
    global connection, cursor, user_email
    bid = input("Enter Borrow ID of the book you want to return: ")
    while not bid.isdigit() or (int(bid) not in user_borrowing): # user_borrowing is an array of bids of user's borrowings from Borrowings()
        print("Invalid Borrow ID. Try again.")
        bid = input("Enter Borrow ID of the book you want to return: ")
    bid = int(bid)

    cursor.execute('''
                SELECT bid
                FROM borrowings
                WHERE bid = ? 
                ''', (bid,)) 
    
    row = cursor.fetchone()
    return_bid = row[0]
    cursor.execute('''
                SELECT IFNULL (b.end_date, date(b.start_date, '+20 days')) AS deadline, b.book_id 
                FROM borrowings b
                WHERE b.member = ? AND b.bid = ? 
                AND b.end_date IS NULL''', (user_email, return_bid)) # Query returns the date of the deadline; start_date + 20
    
    
    row = cursor.fetchall()
    deadline = row[0][0] # double index since its a tuple inside an array
    book_id = row[0][1]

    days = daysPassedDeadline(deadline) # number of days overdue

    # set the penalty if the borrow is late
    if days > 0: 
        setPenalty(return_bid, days)

    updateBorrowings(return_bid) 

    ans = input('Book has been returned. Would you like to write a review for this book? (y/n): ')
    while ans != 'y' and ans != 'n':
        ans = input('Invalid input. Would you like to write a review for this book? (y/n): ')

    if ans == 'y':
        writeReview(book_id)
        
    else:
        print('Returning to main menu.')

def updateBorrowings(return_bid):
    # Function updates user's borrows when returning book
    global user_email, cursor, connection
    cursor.execute('''
                    UPDATE borrowings 
                    SET end_date = DATE('now', 'start of day')
                    WHERE bid = ?
                    AND member = ?
                    AND end_date IS NULL;
                       ''', (return_bid, user_email)) # end_date will be set to today's date
    connection.commit()


def setPenalty(bid, penalty):
    global connection, cursor
    # Since the fine is $1 per day the number of days overdue is equal to the fine

    # First we need to generate a unique PID!
    # To do so, find the current largest one and add one to it
    # In case the table is empty, the first PID generated should be 1
    
    cursor.execute('''
        SELECT IFNULL(MAX(pid), 0)
        FROM penalties
        ''')
    generated_pid = cursor.fetchone()[0] + 1
    cursor.execute('''
        INSERT INTO penalties (pid, bid, amount, paid_amount)
        VALUES (?, ?, ?, ?)
        ''', (generated_pid, bid, penalty, None))
    connection.commit() # save the changes to the db

def daysPassedDeadline(deadline): # calculates number of days late the borrow is overdue by
    today = datetime.date.today()
    deadline = datetime.datetime.strptime(deadline, '%Y-%m-%d').date()
    passed =  (today - deadline).days 
    return passed


def writeReview(book_id):
    # Function handles writing a review for a book after a user returns it
    while True:
        rating = input("On a scale of 1-5, what would you rate this book: ")
        if rating.isdigit() and 1 <= int(rating) <= 5:
            break
        else:
            print("Invalid input. Enter a number between 1 and 5 inclusive")
    rating = int(rating)
    while True:
        reviewText = input("Type out your review of this book (225 characters max): ")
        if len(reviewText) < 225:
            break
        else:
            print("Invalid input. Review must be no more than 225 characters")

    # generate a new rid
    cursor.execute('''
                    SELECT IFNULL(MAX(rid), 0)
                    FROM reviews  
                   ''')
    generated_rid = cursor.fetchone()[0] + 1

    today = datetime.date.today()
    cursor.execute('''
                   INSERT INTO reviews (rid, book_id, member, rating, rtext, rdate)
                   VALUES (?, ?, ?, ?, ?, ?);''',(generated_rid,book_id, user_email, rating, reviewText, today))
    connection.commit()
    print("Your review has been submitted")
    
def main_menu():
    # Function handles logic of main menu
    global connection, cursor, user_email
    print(f'Welcome to the Management System! {user_email}!')
    while True:
        print("Please select an operation from menu below:\n1. Check my profile\n2. Return a book\n3. Search for books\n4. Pay a penalty\n5. Log out\n6. Exit")
        choice = input("Please type in your choice: ")
        if choice == "1":
            myProfile()
        elif choice == "2":
            Borrowings()
        elif choice == "3":
            search_menu()
        elif choice == "4":
            payPenalty()
        elif choice == "5":
            user_email = None
            print("Log out successfully")
            return
        elif choice == "6":
            print("Thank you for using the Management System!")
            exit()
        else:
            print("Invalid input. Please try again!")

def main():
    # main function body
    global connection, cursor, user_email

    if len(sys.argv) != 2: # Take out the 2nd system argument from command line
        print("Usage: python3 program.py <database_name>")
        exit()
    database_name = sys.argv[1]
    path = database_name # This will probably be different for you if you have a different path to the testing db.
    connect(path)

    while True:
        login_menu()
        main_menu()


if __name__=="__main__":
    main()
