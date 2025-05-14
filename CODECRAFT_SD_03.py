import tkinter as tk
from tkinter import messagebox, filedialog
import json
import os
import re
import csv

CONTACTS_FILE = "contacts.json"
edit_index = None

# Email validation function
def is_valid_email(email):
    # Regex to match basic email structure: user@domain.extension
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# Phone number validation function (basic validation)
def is_valid_phone(phone):
    # Check if the phone number consists of digits and optionally includes spaces or hyphens
    pattern = r"^[0-9\s\-\(\)]{10,15}$"  # Allows for 10-15 characters, digits, spaces, hyphens, and parentheses
    return re.match(pattern, phone) is not None

# Load contacts from file
def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r") as file:
            return json.load(file)
    return []

# Save contacts to file
def save_contacts():
    with open(CONTACTS_FILE, "w") as file:
        json.dump(contacts, file, indent=4)

# Add contact
def add_contact():
    global edit_index
    name = entry_name.get().strip()
    phone = entry_phone.get().strip()
    email = entry_email.get().strip()

    if not name or not phone or not email:
        messagebox.showwarning("Input Error", "All fields are required.")
        return

    if not is_valid_email(email):
        messagebox.showwarning("Email Error", "Please enter a valid email address.")
        return

    if not is_valid_phone(phone):
        messagebox.showwarning("Phone Error", "Please enter a valid phone number.")
        return

    new_contact = {"name": name, "phone": phone, "email": email}

    if edit_index is not None:
        contacts[edit_index] = new_contact
        edit_index = None
        messagebox.showinfo("Updated", f"Contact updated successfully!")
    else:
        contacts.append(new_contact)
        messagebox.showinfo("Success", f"Contact '{name}' added successfully!")

    save_contacts()
    update_listbox()
    clear_fields()

# Edit selected contact
def edit_contact():
    global edit_index
    selected = listbox_contacts.curselection()
    if not selected:
        messagebox.showwarning("Selection Error", "No contact selected.")
        return

    edit_index = selected[0]
    contact = contacts[edit_index]

    entry_name.delete(0, tk.END)
    entry_name.insert(0, contact['name'])

    entry_phone.delete(0, tk.END)
    entry_phone.insert(0, contact['phone'])

    entry_email.delete(0, tk.END)
    entry_email.insert(0, contact['email'])

    messagebox.showinfo("Edit Mode", "Modify the fields and click 'Save Changes'.")

# Delete selected contact
def delete_contact():
    global edit_index
    selected = listbox_contacts.curselection()
    if not selected:
        messagebox.showwarning("Selection Error", "No contact selected.")
        return

    index = selected[0]
    contact = contacts[index]
    confirm = messagebox.askyesno("Confirm Delete", f"Delete contact '{contact['name']}'?")
    if confirm:
        contacts.pop(index)
        save_contacts()
        update_listbox()
        if edit_index == index:
            edit_index = None
        clear_fields()

# Search contact by name
def search_contact():
    name = entry_name.get().strip().lower()
    filtered = [c for c in contacts if c["name"].lower() == name]

    listbox_contacts.delete(0, tk.END)
    if filtered:
        for contact in filtered:
            listbox_contacts.insert(tk.END, f"{contact['name']} | {contact['phone']} | {contact['email']}")
    else:
        messagebox.showinfo("Search Result", "No contact found with that name.")

# View all contacts
def update_listbox():
    listbox_contacts.delete(0, tk.END)
    for contact in contacts:
        listbox_contacts.insert(tk.END, f"{contact['name']} | {contact['phone']} | {contact['email']}")

# Clear input fields
def clear_fields():
    global edit_index
    entry_name.delete(0, tk.END)
    entry_phone.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    edit_index = None

# Sort contacts by name
def sort_by_name():
    contacts.sort(key=lambda x: x["name"].lower())
    update_listbox()

# Sort contacts by email
def sort_by_email():
    contacts.sort(key=lambda x: x["email"].lower())
    update_listbox()

# Export contacts to CSV
def export_to_csv():
    # Open a file dialog to select location and filename
    file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    
    if not file_path:
        return  # If the user cancels the file dialog, exit the function

    try:
        with open(file_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            # Write the header
            writer.writerow(["Name", "Phone", "Email"])
            # Write each contact's data
            for contact in contacts:
                writer.writerow([contact["name"], contact["phone"], contact["email"]])
        
        messagebox.showinfo("Export Successful", f"Contacts exported successfully to {file_path}")
    except Exception as e:
        messagebox.showerror("Export Error", f"An error occurred: {e}")

# Import contacts from CSV
def import_from_csv():
    # Open a file dialog to select a CSV file
    file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    
    if not file_path:
        return  # If the user cancels the file dialog, exit the function

    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            headers = next(reader)  # Skip header row
            
            # Parse and add contacts from the CSV file
            for row in reader:
                if len(row) < 3:  # Ensure the row has enough data
                    messagebox.showwarning("CSV Format Error", "Invalid CSV format. Each row must have name, phone, and email.")
                    return
                name, phone, email = row
                # Check for duplicates before adding
                if any(contact["name"] == name or contact["email"] == email for contact in contacts):
                    messagebox.showinfo("Duplicate Detected", f"Skipping duplicate contact: {name} ({email})")
                elif not is_valid_phone(phone):
                    messagebox.showwarning("Phone Error", f"Invalid phone number for contact: {name}")
                elif not is_valid_email(email):  # Validate email before adding
                    messagebox.showwarning("Email Error", f"Invalid email for contact: {name}")
                else:
                    contacts.append({"name": name, "phone": phone, "email": email})
        
        save_contacts()
        update_listbox()
        messagebox.showinfo("Import Successful", f"Contacts imported successfully from {file_path}")
    
    except Exception as e:
        messagebox.showerror("Import Error", f"An error occurred: {e}")

# Initialize GUI
contacts = load_contacts()
root = tk.Tk()
root.title("Contact Management System")
root.geometry("520x520")
root.resizable(False, False)

# Input fields
tk.Label(root, text="Name").grid(row=0, column=0, padx=10, pady=5, sticky="w")
entry_name = tk.Entry(root, width=30)
entry_name.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Phone").grid(row=1, column=0, padx=10, pady=5, sticky="w")
entry_phone = tk.Entry(root, width=30)
entry_phone.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Email").grid(row=2, column=0, padx=10, pady=5, sticky="w")
entry_email = tk.Entry(root, width=30)
entry_email.grid(row=2, column=1, padx=10, pady=5)

# Buttons
tk.Button(root, text="Add / Save Changes", width=18, command=add_contact).grid(row=3, column=0, padx=10, pady=10)
tk.Button(root, text="Search", width=18, command=search_contact).grid(row=3, column=1, padx=10, pady=10)
tk.Button(root, text="Delete Selected", width=18, command=delete_contact).grid(row=4, column=0, padx=10, pady=5)
tk.Button(root, text="Edit Selected", width=18, command=edit_contact).grid(row=4, column=1, padx=10, pady=5)
tk.Button(root, text="Sort by Name", width=18, command=sort_by_name).grid(row=5, column=0, padx=10, pady=5)
tk.Button(root, text="Sort by Email", width=18, command=sort_by_email).grid(row=5, column=1, padx=10, pady=5)
tk.Button(root, text="View All", width=18, command=update_listbox).grid(row=6, column=0, columnspan=2, pady=5)
tk.Button(root, text="Export to CSV", width=18, command=export_to_csv).grid(row=7, column=0, columnspan=2, pady=5)
tk.Button(root, text="Import from CSV", width=18, command=import_from_csv).grid(row=8, column=0, columnspan=2, pady=5)

# Listbox
listbox_contacts = tk.Listbox(root, width=70)
listbox_contacts.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
update_listbox()

root.mainloop()
