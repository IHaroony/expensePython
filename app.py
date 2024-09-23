from flask import Flask
from flask_socketio import SocketIO
import sys
import io

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global context to hold the expenses and state
execution_context = {
    'output': io.StringIO(),  # For capturing the print output
    'expenses': [],  # This will hold the list of expenses
    'current_step': 0,  # Track the current step
    'new_expense': {}  # Temporary storage for the new expense
}

# Helper function to print the options menu
def show_menu():
    return """
: What would you like to do? :

                           1. Add an Expense

     2.View All Expenses

 3. View Total Spent

 4.Exit





                            Please choose your option?:
                            """

# Handle each option in the menu
def process_menu_option(option):
    if option == '1' or option.lower() == 'add':
        execution_context['current_step'] = 1  # Start adding an expense
        return "Please enter the amount for your expense:"

    elif option == '2' or option.lower() == 'view':
        if not execution_context['expenses']:
            return "No expenses recorded yet."
        output = "List of all expenses:\n"
        for idx, expense in enumerate(execution_context['expenses'], start=1):
            output += f"{idx}. Amount: ${expense['amount']:.2f}, Category: {expense['category']}, Date: {expense['date']}, Quantity: {expense['quantity']}\n"
        return output + "\n" + show_menu()  # Show menu again after viewing expenses

    elif option == '3' or option.lower() == 'total':
        total = sum(expense['amount'] * expense['quantity'] for expense in execution_context['expenses'])
        return f"Total amount spent: ${total:.2f}\n" + show_menu()

    elif option == '4' or option.lower() == 'exit':
        return "Thanks for using the Expense Tracker! Goodbye."

    else:
        return "Invalid option. Please select 1, 2, 3, or 4.\n" + show_menu()

# Handle input from terminal
@socketio.on('input')
def handle_input(data):
    step = execution_context['current_step']
    data = data.strip().lower()

    if step == 0:
        # We are in the menu
        output = process_menu_option(data)
        if "Goodbye" in output:
            socketio.emit('output', output)
            return
        else:
            socketio.emit('output', output)
            return

    if step == 1:
        # Expect amount
        try:
            amount = float(data)
            execution_context['new_expense']['amount'] = amount
            execution_context['current_step'] = 2
            output = "Amount received. Please enter the category (e.g., Food, Transport, Entertainment):"
        except ValueError:
            output = "Invalid amount. Please enter a valid number:"
        socketio.emit('output', output)
        return

    elif step == 2:
        # Expect category
        execution_context['new_expense']['category'] = data
        execution_context['current_step'] = 3
        output = "Category received. Please enter the date (DD/MM/YYYY):"
        socketio.emit('output', output)
        return

    elif step == 3:
        # Expect date
        execution_context['new_expense']['date'] = data
        execution_context['current_step'] = 4
        output = "Date received. Please enter the quantity:"
        socketio.emit('output', output)
        return

    elif step == 4:
        # Expect quantity
        try:
            quantity = float(data)
            execution_context['new_expense']['quantity'] = quantity
            execution_context['expenses'].append(execution_context['new_expense'].copy())  # Add the expense to the list
            execution_context['new_expense'] = {}  # Reset for next expense
            execution_context['current_step'] = 0  # Go back to menu
            output = "Expense added successfully!\n" + show_menu()
        except ValueError:
            output = "Invalid quantity. Please enter a valid number:"
        socketio.emit('output', output)
        return

# Start the expense tracker by showing the menu
@socketio.on('start_code_execution')
def handle_start_execution():
    output = "Welcome to the Expense Tracker!\n" + show_menu()
    socketio.emit('output', output)

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000, debug=True)
