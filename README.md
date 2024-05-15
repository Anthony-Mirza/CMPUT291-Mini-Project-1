# CMPUT 291 Mini Project 1 - Winter 2024  
**Group member names and ccids:**  
  Anthony Mirza, amirza2  
  Rong Liu, rongjia2  
  Tolu Lajide, tlajide

  ---

# Group work break-down strategy
| Group Member   | Tasks   |
|------------|------------|
| Anthony Mirza | Completed _Member Profile_ and _Pay a Penalty_ system functionalities for user interface. |
| Rong Liu | Completed _Login Screen_ and _Search for books_ functionalities. |
| Tolu Lajide | Completed _Return a book_ functionality. |

| Group Member   | Progress   | Status   |
|------------|------------|------------|
| Anthony Mirza | _Member Profile_ |Done|
| Anthony Mirza | _Pay a Penalty_ |Done|
| Rong Liu | _Login Screen_ |Done|
| Rong Liu |  _Search for books_ |Done|
| Tolu Lajide | _Return a book_ |Done|

| Group Member | Tasks | Time Estimate (in hours) |
|----------|----------|----------|
| Anthony Mirza | Completed _Member Profile_ and _Pay a Penalty_ system functionalities for user interface. Fixed and integrated _Returning a Book_ functionality into our program. Completed extensive testing by generating test data and using it to check that the program's output was correct and handled all conceivable edge cases. Additionally, I wrote documentation for code I was responsible for. | 20 |
| Rong Liu | Completed _Login Screen_ and _Search For Books_ functionalities also the main menu interface. Added input guards for the majority of functions in the program (penalty paying and book returning, etc.) Completed testing by creating different test cases and checked the program output to ensure edge cases (inputs) are covered. Participated in writing documentation. | 20 |
| Tolu Lajide | Worked on displaying current borrowings, returning a book to the system, calculating the late penalty and writiing the review for returned books. Completed testing by providing different input the program and checked if the output was correct. | 15 |

---
# Method of group coordination

Our group's primary means of coordination was communicating through Discord and in-person meetings. We communicated daily to discuss our progress and any difficulties we were facing. We initially divided the workload as follows: Anthony was responsible for _Member Profile_, Rong for _Logging And Signing In_ and  _Search for books_, and Tolu for _Returing a Book_. Once a member was finished with their task, they moved on to implementing another system functionality that was not completed yet. We implemented the system's functionalities in the sequential order that they were listed in the project's description on eClass. For more information on each group member's task, please see the table above. 

---
# Code execution guide

1. First, to run the program make sure that the database file is within the same folder as `mini-project1.py` and type  `python3 mini-project1.py <database-name>` in the command prompt.

2.  Upon starting the program the login menu will be displayed. You can enter 1, 2, or 3 to respectively log in, sign up, or exit the program.
    - If you type 1, the login menu will require you to enter a valid email address and password. After succesfully logging in you will be directed to the main menu.
    - If you type 2 you will be prompted to create an account with unique email and other personal information. After successfully creating an account, you will be directed to the main menu.
    - If you type 3, the program will gracefully end.

3. At main menu, you will have 6 options. Type 1 to check out your profile information, type 2 to return a book that you have borrowed, type 3 to search for a book and optionally borrow it, type 4 to pay a penalty, type 5 to log out and go back to the login menu, and type 6 to exit the program.
   
    - If you type 1, a window will pop out, with all your borrowing, penalty and personal information.
    
    - If you type 2, you will see all the books that you have currently borrowed. Enter 1 then enter the **bid** of the specific borrowing you want to return to return a book, or enter 2 to return to the main menu. After returning a book, you can optionally choose to leave an review by typing y/n.
    
    - If you type 3, you will then be asked to type in a keyword and the first 5 books that match the condition will be displayed. You can enter 1 to check another 5 books that match the search keyword on the next page. Enter 2 then enter the **book_id** of the specific book you want to borrow to borrow a book (if it is available), or enter 3 to return to the main menu.
    
    - If you type 4, you will see a list of your penalties. If you have no penalties a message will indicate so and you will remain in the main menu. Otherwise, You can type in the **pid** of the specific penalty you want to pay from the list of penalites displayed and enter the amount to pay a penalty in full or partially. If you enter 0, you will return to the main menu.
    
    - If you type 5, you will log out your account and return to the login menu.
    
    - If you type 6, you will exit the program.

---
# Names of anyone you have collaborated with (as much as it is allowed within the course policy) or a line saying that you did not collaborate with anyone else.

Our group did not collaborate with anyone else.

---

# Sources used

CASE in SQL: https://www.w3schools.com/sql/sql_case.asp

# Extra documentation

We don't have any decision or code that is beyond or different from what is required other than adding input guards to all input function calls.
