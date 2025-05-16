import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
import os

main = tk.Tk()
main.title("CEREBRO | X-Men Universe Database")
main.geometry("600x700")

# Main title 
label_greeting = tk.Label(main, text="CEREBRO", font=('Arial', 16, "bold"))
label_greeting.grid(pady=20)
# Main subtitle
label_subgreeting = tk.Label(main, text="Create your own mutant database!")

# Input Frame - Creates an entry in the mutant.db
frame_input = tk.Frame(main, padx=10, pady=10)

tk.Label(frame_input, text="Hero/Villian Name:").grid(row=0, column=0, sticky='e')
entry_name = tk.Entry(frame_input, width=40)
entry_name.grid(row=0, column=1)

tk.Label(frame_input, text="Powers:").grid(row=1, column=0, sticky='e')
entry_power = tk.Entry(frame_input, width=40)
entry_power.grid(row=1, column=1)

tk.Label(frame_input, text="Affiliation:").grid(row=2, column=0, sticky='e')
entry_affiliation = tk.Entry(frame_input, width=40)
entry_affiliation.grid(row=2, column=1)

button_add = tk.Button(frame_input, text="Add Mutant", command=lambda: \
                       add_mutant(entry_name.get(), entry_power.get(), entry_affiliation.get()))
button_add.grid(row=3, columnspan=2, pady=10)

# Search Frame - Enter a keyword to search mutant.db
frame_search = tk.Frame(main, padx=10, pady=10)

tk.Label(frame_search, text="Search:").grid(row=0, column=0, sticky='e')
entry_search = tk.Entry(frame_search)
entry_search.grid(row=0, column=1)

# Search Button
button_search = tk.Button(frame_search, text="Search", command=lambda: search_mutant(entry_search.get()))
button_search.grid(row=0, column=2, padx=5)

# Show All Button - Display all entries in the mutant.dv
button_show_all = tk.Button(frame_search, text="Show All", command=lambda: search_mutant(""))
button_show_all.grid(row=0, column=3, padx=5)

# Edit Frame - Used to edit an existing entry
edit_button = tk.Button(frame_search, text="Edit Selected Mutant", command=lambda: edit_mutant())
edit_button.grid(row=1, columnspan=3, pady=10)  # Place the Edit button below Search

# Delete Selected Mutant Button
delete_button = tk.Button(frame_search, text="Delete Selected Mutant", command=lambda: delete_mutant())
delete_button.grid(row=2, columnspan=3, pady=10)

# Treeview Frame
frame_tree = tk.Frame(main)

global tree  # Declare 'tree' as global to use it in `mutant`

# This displays the mutant info in the GUI in a table format
tree = ttk.Treeview(frame_tree, columns=('ID', 'Name', 'Power', 'Affiliation'), show='headings')
tree.heading('ID', text='ID')
tree.heading('Name', text='Mutant Name')
tree.heading('Power', text='Power')
tree.heading('Affiliation', text='Affiliation')

# Edit the treeview's column width
tree.column('ID', width=75, minwidth=20, stretch=False)
tree.column('Name', width=125, minwidth=20, stretch=True)
tree.column('Power', width=175, minwidth=20, stretch=True)
tree.column('Affiliation', width=75, minwidth=20, stretch=True)

# This creates the scollbar for the table displey
vsb = ttk.Scrollbar(frame_tree, orient="vertical", command=tree.yview)
hsb = ttk.Scrollbar(frame_tree, orient="horizontal", command=tree.xview)

tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
tree.grid(row=0, column=0, sticky='nsew')
vsb.grid(row=0, column=1, sticky='ns')
hsb.grid(row=1, column=0, sticky='ew')

frame_tree.grid_rowconfigure(0, weight=1)
frame_tree.grid_columnconfigure(0, weight=1)

# Creates the database in the same folder as the python script
def get_db_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, 'mutant.db')

# Sets up the mutant.db
def setup_database():
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS mutant (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            power TEXT,
            affiliation TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Adds a mutant to the mutant.db
def add_mutant(name, power, affiliation):
    if not name:
        messagebox.showerror("Error", "Mutant name is required!")
        return

    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('INSERT INTO mutant (name, power, affiliation) VALUES (?, ?, ?)', (name, power, affiliation))

    entry_name.delete(0, tk.END)
    entry_power.delete(0, tk.END)
    entry_affiliation.delete(0, tk.END)

    conn.commit()
    conn.close()

# The function that searches through mutant.db
def search_mutant(keyword):
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
     # Cleaner - Searches everywhere for the keyword
    query = '''
        SELECT * FROM  mutant
        WHERE name LIKE ? OR power LIKE ? OR affiliation LIKE ?
    '''
    
    if keyword:
        # Search using the keyword
        cursor.execute(query, ('%'+keyword+'%', '%'+keyword+'%', '%'+keyword+'%',))
    else:
        # Show all entries if no keyword is provided
        cursor.execute('SELECT * FROM mutant')
    
    # This retrieves all rows of the query and returns them as a list of tuples
    results = cursor.fetchall()

    # Removes rows from the table display
    for widget in tree.get_children():
        tree.delete(widget)

    # Inserts rows from the mutant.db into the table view
    for result in results:
        tree.insert('', 'end', values=result)
    conn.close()

def edit_mutant():
    # Get selected item
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a mutant to edit!")
        return

    selected_item = selected_item[0]
    mutant_id = tree.item(selected_item, 'values')[0]

    # Fetch current data
    conn = sqlite3.connect(get_db_path())
    cursor = conn.cursor()
    cursor.execute('SELECT name, power, affiliation FROM mutant WHERE id=?', (mutant_id,))
    result = cursor.fetchone()
    if not result:
        messagebox.showerror("Error", "Mutant not found!")
        return

    # Populate fields with current data
    entry_name.delete(0, tk.END)
    entry_power.delete(0, tk.END)
    entry_affiliation.delete(0, tk.END)

    entry_name.insert(0, result[0])
    entry_power.insert(0, result[1] or '')
    entry_affiliation.insert(0, result[2] or '')

    # Update button to save changes
    def update_mutant():
        new_name = entry_name.get()
        new_power = entry_power.get()
        new_affiliation = entry_affiliation.get()

        if not new_name:
            messagebox.showerror("Error", "Mutant name is required!")
            return

        conn.execute('UPDATE mutant SET name=?, power=?, affiliation=? WHERE id=?',
                     (new_name, new_power, new_affiliation, mutant_id))
        conn.commit()
        conn.close()

        search_mutant(entry_search.get())  # Refresh the view to see changes
        messagebox.showinfo("Success", "Mutant updated successfully!")

    update_button = tk.Button(frame_input, text="Update Mutant", command=update_mutant)
    button_add.grid_forget()  # Hide the original Add button
    update_button.grid(row=3, columnspan=2, pady=10)

# Delete an entry from the mutant.db
def delete_mutant():
    # Get selected item
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Error", "Please select a mutant to delete!")
        return

    selected_item = selected_item[0]
    mutant_id = tree.item(selected_item, 'values')[0]

    # Confirm deletion
    if messagebox.askyesno("Delete Mutant", f"Are you sure you want to delete the mutant with ID {mutant_id}?"):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute('DELETE FROM mutant WHERE id=?', (mutant_id,))
        conn.commit()

        # Remove from Treeview
        tree.delete(selected_item)

        messagebox.showinfo("Success", "Mutant deleted successfully!")
    else:
        messagebox.showinfo("Cancelled", "Deletion cancelled.")

    conn.close()

# The layout of the GUI
label_greeting.pack(side=tk.TOP, fill='x', pady=(15, 0))
label_subgreeting.pack(side=tk.TOP, fill='x')
frame_input.pack(pady=20)
frame_search.pack()
frame_tree.pack(pady=20, fill='both', expand=True)
setup_database()
main.mainloop()