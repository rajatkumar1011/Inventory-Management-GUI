import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import database

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Inventory Management System")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        self.current_user_id = None
        
        # Modern styling configuration
        self.setup_styles()
        
        # Container for pages
        container = ttk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # Initialize all pages
        for F in (LoginPage, RegisterPage, InventoryPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("LoginPage")
    
    def setup_styles(self):
        """Configure modern ttk styles"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Title style
        style.configure("Title.TLabel", font=("Segoe UI", 28, "bold"), foreground="#2c3e50")
        
        # Header style
        style.configure("Header.TLabel", font=("Segoe UI", 18, "bold"), foreground="#34495e")
        
        # Button styles
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"), padding=10)
        style.map("Primary.TButton",
                  background=[("active", "#3498db"), ("!disabled", "#3498db")],
                  foreground=[("active", "white"), ("!disabled", "white")])
        
        style.configure("Secondary.TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Link.TButton", font=("Segoe UI", 9), foreground="#3498db")
        
        # Treeview styles
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=30)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#ecf0f1")
        style.map("Treeview", background=[("selected", "#3498db")])
        
        # Entry style
        style.configure("Custom.TEntry", padding=8, font=("Segoe UI", 10))
        
        # LabelFrame style
        style.configure("TLabelframe", font=("Segoe UI", 11, "bold"), borderwidth=1)
        style.configure("TLabelframe.Label", font=("Segoe UI", 11, "bold"), foreground="#34495e")
    
    def show_frame(self, page_name):
        """Show a specific frame"""
        frame = self.frames[page_name]
        
        if page_name == "InventoryPage":
            frame.refresh_data()
            
        frame.tkraise()


class LoginPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main container with padding
        main_container = ttk.Frame(self, padding="40")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ttk.Label(main_container, text="Inventory Login", style="Title.TLabel")
        title.pack(pady=(0, 30))
        
        # Form container
        form_frame = ttk.Frame(main_container)
        form_frame.pack()
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Segoe UI", 10)).pack(pady=(10, 5), anchor='w')
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                        style="Custom.TEntry", width=35, font=("Segoe UI", 10))
        self.username_entry.pack(pady=5, ipady=6)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Segoe UI", 10)).pack(pady=(15, 5), anchor='w')
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                        style="Custom.TEntry", width=35, font=("Segoe UI", 10),
                                        show="*")
        self.password_entry.pack(pady=5, ipady=6)
        self.password_entry.bind("<Return>", self.attempt_login)
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(20, 0))
        
        login_button = ttk.Button(button_frame, text="Login", 
                                  command=self.attempt_login, 
                                  style="Primary.TButton", width=25)
        login_button.pack(pady=10, fill='x')
        
        register_button = ttk.Button(button_frame, text="Don't have an account? Register",
                                     command=lambda: controller.show_frame("RegisterPage"),
                                     style="Link.TButton")
        register_button.pack(pady=5)
        
        # Focus on username entry
        self.username_entry.focus()
    
    def attempt_login(self, event=None):
        """Handle login attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        
        if not username or not password:
            messagebox.showerror("Login Error", "Please enter both username and password.")
            return
        
        try:
            user_id = database.check_user(username, password)
            
            if user_id:
                self.controller.current_user_id = user_id
                self.username_var.set("")
                self.password_var.set("")
                self.controller.show_frame("InventoryPage")
            else:
                messagebox.showerror("Login Error", "Invalid username or password.")
                self.password_var.set("")
                self.password_entry.focus()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during login: {str(e)}")


class RegisterPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Main container
        main_container = ttk.Frame(self, padding="40")
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ttk.Label(main_container, text="Create Account", style="Title.TLabel")
        title.pack(pady=(0, 30))
        
        # Form container
        form_frame = ttk.Frame(main_container)
        form_frame.pack()
        
        # Username field
        ttk.Label(form_frame, text="Username:", font=("Segoe UI", 10)).pack(pady=(10, 5), anchor='w')
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(form_frame, textvariable=self.username_var, 
                                        style="Custom.TEntry", width=35, font=("Segoe UI", 10))
        self.username_entry.pack(pady=5, ipady=6)
        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus())
        
        # Password field
        ttk.Label(form_frame, text="Password:", font=("Segoe UI", 10)).pack(pady=(15, 5), anchor='w')
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(form_frame, textvariable=self.password_var, 
                                       style="Custom.TEntry", width=35, font=("Segoe UI", 10),
                                       show="*")
        self.password_entry.pack(pady=5, ipady=6)
        self.password_entry.bind("<Return>", lambda e: self.confirm_pass_entry.focus())
        
        # Confirm password field
        ttk.Label(form_frame, text="Confirm Password:", font=("Segoe UI", 10)).pack(pady=(15, 5), anchor='w')
        self.confirm_pass_var = tk.StringVar()
        self.confirm_pass_entry = ttk.Entry(form_frame, textvariable=self.confirm_pass_var, 
                                           style="Custom.TEntry", width=35, font=("Segoe UI", 10),
                                           show="*")
        self.confirm_pass_entry.pack(pady=5, ipady=6)
        self.confirm_pass_entry.bind("<Return>", self.attempt_register)
        
        # Buttons
        button_frame = ttk.Frame(main_container)
        button_frame.pack(pady=(20, 0))
        
        register_button = ttk.Button(button_frame, text="Register", 
                                     command=self.attempt_register, 
                                     style="Primary.TButton", width=25)
        register_button.pack(pady=10, fill='x')
        
        login_button = ttk.Button(button_frame, text="Already have an account? Login",
                                 command=lambda: controller.show_frame("LoginPage"),
                                 style="Link.TButton")
        login_button.pack(pady=5)
        
        # Focus on username entry
        self.username_entry.focus()
    
    def attempt_register(self, event=None):
        """Handle registration attempt"""
        username = self.username_var.get().strip()
        password = self.password_var.get()
        confirm_pass = self.confirm_pass_var.get()
        
        if not username or not password or not confirm_pass:
            messagebox.showerror("Input Error", "Please fill all fields.")
            return
        
        if len(username) < 3:
            messagebox.showerror("Input Error", "Username must be at least 3 characters long.")
            return
        
        if len(password) < 4:
            messagebox.showerror("Input Error", "Password must be at least 4 characters long.")
            return
        
        if password != confirm_pass:
            messagebox.showerror("Input Error", "Passwords do not match.")
            self.confirm_pass_var.set("")
            self.confirm_pass_entry.focus()
            return
        
        try:
            success = database.register_user(username, password)
            if success:
                messagebox.showinfo("Success", "Account created successfully! Please login.")
                self.username_var.set("")
                self.password_var.set("")
                self.confirm_pass_var.set("")
                self.controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Registration Error", "Username already exists. Please choose a different username.")
                self.username_var.focus()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during registration: {str(e)}")


class InventoryPage(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        # Validation commands
        self.vcmd_numeric = (self.register(self._validate_numeric), '%P')
        self.vcmd_float = (self.register(self._validate_float), '%P')
        
        # Main container with padding
        self.main_frame = ttk.Frame(self, padding="20")
        self.main_frame.pack(fill='both', expand=True)
        
        # Header section
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill='x', pady=(0, 20))
        
        self.header_label = ttk.Label(self.header_frame, text="Inventory Management", style="Header.TLabel")
        self.header_label.pack(side='left')
        
        self.logout_btn = ttk.Button(self.header_frame, text="Logout",
                                     command=self.logout, style="Secondary.TButton")
        self.logout_btn.pack(side='right')
        
        # Product entry section
        self.entry_frame = ttk.LabelFrame(self.main_frame, text="Product Details", padding="20")
        self.entry_frame.pack(fill='x', pady=(0, 15))
        self.entry_frame.columnconfigure(1, weight=1)
        self.entry_frame.columnconfigure(3, weight=1)
        
        # Product name
        ttk.Label(self.entry_frame, text="Product Name:", font=("Segoe UI", 10)).grid(
            row=0, column=0, padx=10, pady=10, sticky='w')
        self.product_name = tk.StringVar()
        self.name_entry = ttk.Entry(self.entry_frame, textvariable=self.product_name, 
                                   style="Custom.TEntry", width=30, font=("Segoe UI", 10))
        self.name_entry.grid(row=0, column=1, padx=10, pady=10, sticky='ew')
        self.name_entry.bind("<Return>", lambda e: self.quantity_entry.focus())
        
        # Quantity
        ttk.Label(self.entry_frame, text="Quantity:", font=("Segoe UI", 10)).grid(
            row=0, column=2, padx=10, pady=10, sticky='w')
        self.quantity = tk.StringVar(value='0')
        self.quantity_entry = ttk.Entry(self.entry_frame, textvariable=self.quantity, 
                                        style="Custom.TEntry", width=20, font=("Segoe UI", 10),
                                        validate='key', validatecommand=self.vcmd_numeric)
        self.quantity_entry.grid(row=0, column=3, padx=10, pady=10, sticky='ew')
        self.quantity_entry.bind("<Return>", lambda e: self.price_entry.focus())
        
        # Price
        ttk.Label(self.entry_frame, text="Price ($):", font=("Segoe UI", 10)).grid(
            row=1, column=0, padx=10, pady=10, sticky='w')
        self.price = tk.StringVar(value='0.00')
        self.price_entry = ttk.Entry(self.entry_frame, textvariable=self.price, 
                                    style="Custom.TEntry", width=20, font=("Segoe UI", 10),
                                    validate='key', validatecommand=self.vcmd_float)
        self.price_entry.grid(row=1, column=1, padx=10, pady=10, sticky='ew')
        self.price_entry.bind("<Return>", lambda e: self.add_item() if self.add_btn['state'] == 'normal' else None)
        
        # Button section
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(fill='x', pady=(0, 15))
        
        self.add_btn = ttk.Button(self.button_frame, text="Add Product", 
                                  command=self.add_item, style="Primary.TButton")
        self.add_btn.grid(row=0, column=0, padx=5, pady=5, sticky='w')
        
        self.update_btn = ttk.Button(self.button_frame, text="Update Product", 
                                     command=self.update_item, style="Secondary.TButton")
        self.update_btn.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        self.delete_btn = ttk.Button(self.button_frame, text="Delete Product", 
                                    command=self.delete_item, style="Secondary.TButton")
        self.delete_btn.grid(row=0, column=2, padx=5, pady=5, sticky='w')
        
        self.clear_btn = ttk.Button(self.button_frame, text="Clear Fields", 
                                   command=self.clear_fields, style="Secondary.TButton")
        self.clear_btn.grid(row=0, column=3, padx=5, pady=5, sticky='w')
        
        # Treeview section with scrollbar
        tree_container = ttk.Frame(self.main_frame)
        tree_container.pack(fill='both', expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(tree_container, columns=('ID', 'Name', 'Quantity', 'Price'), 
                                show='headings', style="Treeview")
        
        # Configure columns
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Product Name')
        self.tree.heading('Quantity', text='Quantity')
        self.tree.heading('Price', text='Price ($)')
        
        self.tree.column('ID', width=60, anchor='center', stretch=False)
        self.tree.column('Name', width=400, anchor='w')
        self.tree.column('Quantity', width=150, anchor='center')
        self.tree.column('Price', width=150, anchor='e')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side='right', fill='y')
        self.tree.pack(side='left', fill='both', expand=True)
        
        # Configure row colors
        self.tree.tag_configure('even', background='#f8f9fa')
        self.tree.tag_configure('odd', background='white')
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.select_item)
        self.tree.bind('<Double-1>', lambda e: self.select_item())
        
        # Initialize state
        self.selected_item_id = None
        self._update_button_states('clear')
    
    def refresh_data(self):
        """Refresh inventory data"""
        if not self.controller.current_user_id:
            self.logout()
            return
        self.populate_list()
        self.clear_fields()
    
    def logout(self):
        """Handle logout"""
        self.controller.current_user_id = None
        self.clear_fields()
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.controller.show_frame("LoginPage")
    
    def _validate_numeric(self, P):
        """Validate numeric input"""
        if P == "" or P == "0":
            return True
        return P.isdigit() and int(P) >= 0
    
    def _validate_float(self, P):
        """Validate float input"""
        if P == "" or P == "0" or P == "0.":
            return True
        try:
            float(P)
            return float(P) >= 0
        except ValueError:
            return False
    
    def _update_button_states(self, state):
        """Update button states based on selection"""
        if state == 'selected':
            self.add_btn.config(state='disabled')
            self.update_btn.config(state='normal')
            self.delete_btn.config(state='normal')
        elif state == 'clear':
            self.add_btn.config(state='normal')
            self.update_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')
    
    def populate_list(self):
        """Populate treeview with products"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if not self.controller.current_user_id:
            return
        
        try:
            products = database.view_products(self.controller.current_user_id)
            
            for i, product in enumerate(products):
                product_id, name, quantity, price = product
                tag = 'even' if i % 2 == 0 else 'odd'
                # Format price to 2 decimal places
                formatted_price = f"{float(price):.2f}"
                self.tree.insert('', 'end', values=(product_id, name, quantity, formatted_price), 
                               tags=(tag,))
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to load products: {str(e)}")
    
    def add_item(self):
        """Add new product"""
        name = self.product_name.get().strip()
        quantity_str = self.quantity.get().strip()
        price_str = self.price.get().strip()
        
        # Validation
        if not name:
            messagebox.showerror("Input Error", "Product name cannot be empty.")
            self.name_entry.focus()
            return
        
        if not quantity_str or quantity_str == "0":
            messagebox.showerror("Input Error", "Please enter a valid quantity (greater than 0).")
            self.quantity_entry.focus()
            return
        
        if not price_str or price_str == "0" or price_str == "0.0" or price_str == "0.00":
            messagebox.showerror("Input Error", "Please enter a valid price (greater than 0).")
            self.price_entry.focus()
            return
        
        try:
            quantity = int(quantity_str)
            price = float(price_str)
            
            if quantity <= 0:
                raise ValueError("Quantity must be greater than 0")
            if price <= 0:
                raise ValueError("Price must be greater than 0")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return
        
        if not self.controller.current_user_id:
            messagebox.showerror("Error", "No user logged in. Please login again.")
            self.logout()
            return
        
        try:
            database.add_product(self.controller.current_user_id, name, quantity, price)
            messagebox.showinfo("Success", "Product added successfully!")
            self.populate_list()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to add product: {str(e)}")
    
    def select_item(self, event=None):
        """Handle item selection in treeview"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        try:
            selected_item = selected_items[0]
            item_values = self.tree.item(selected_item)['values']
            
            if len(item_values) >= 4:
                self.selected_item_id = item_values[0]
                self.product_name.set(item_values[1])
                self.quantity.set(str(item_values[2]))
                # Format price if needed
                price_val = item_values[3]
                try:
                    float_price = float(price_val)
                    self.price.set(f"{float_price:.2f}")
                except:
                    self.price.set(str(price_val))
                
                self._update_button_states('selected')
        except (IndexError, ValueError) as e:
            pass
    
    def update_item(self):
        """Update selected product"""
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select a product to update.")
            return
        
        name = self.product_name.get().strip()
        quantity_str = self.quantity.get().strip()
        price_str = self.price.get().strip()
        
        if not name:
            messagebox.showerror("Input Error", "Product name cannot be empty.")
            self.name_entry.focus()
            return
        
        if not quantity_str or quantity_str == "0":
            messagebox.showerror("Input Error", "Please enter a valid quantity (greater than 0).")
            self.quantity_entry.focus()
            return
        
        if not price_str or price_str == "0" or price_str == "0.0" or price_str == "0.00":
            messagebox.showerror("Input Error", "Please enter a valid price (greater than 0).")
            self.price_entry.focus()
            return
        
        try:
            quantity = int(quantity_str)
            price = float(price_str)
            
            if quantity < 0:
                raise ValueError("Quantity cannot be negative")
            if price < 0:
                raise ValueError("Price cannot be negative")
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input: {str(e)}")
            return
        
        try:
            database.update_product(self.selected_item_id, name, quantity, price)
            messagebox.showinfo("Success", "Product updated successfully!")
            self.populate_list()
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to update product: {str(e)}")
    
    def delete_item(self):
        """Delete selected product"""
        if not self.selected_item_id:
            messagebox.showerror("Error", "Please select a product to delete.")
            return
        
        product_name = self.product_name.get()
        if messagebox.askyesno("Confirm Delete", 
                               f"Are you sure you want to delete '{product_name}'?"):
            try:
                database.delete_product(self.selected_item_id)
                messagebox.showinfo("Success", "Product deleted successfully!")
                self.populate_list()
                self.clear_fields()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to delete product: {str(e)}")
    
    def clear_fields(self):
        """Clear input fields and reset state"""
        self.product_name.set("")
        self.quantity.set("0")
        self.price.set("0.00")
        self.selected_item_id = None
        
        # Clear treeview selection
        for item in self.tree.selection():
            self.tree.selection_remove(item)
        
        self._update_button_states('clear')
        self.name_entry.focus()


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()