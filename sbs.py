import tkinter as tk
from tkinter import ttk, messagebox
import json, os, datetime

# --- File Setup ---
inventory_file = "inventory.json"
sales_file = "sales.json"
customers_file = "customers.json"

for file in [inventory_file, sales_file, customers_file]:
    if not os.path.exists(file):
        with open(file, "w") as f:
            json.dump({} if file != sales_file else {"sales": [], "total_sales": 0}, f)

def load_data(file):
    with open(file, "r") as f:
        return json.load(f)

def save_data(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

# --- Load default products if inventory is empty ---
if os.path.getsize(inventory_file) == 0:
    default_inventory = {
        "Helmet": {"price": 1200, "stock": 15},
        "Gloves": {"price": 500, "stock": 30},
        "Chain Oil": {"price": 250, "stock": 20},
        "Spark Plug": {"price": 180, "stock": 25},
        "Tyre": {"price": 1800, "stock": 10},
        "Brake Pad": {"price": 400, "stock": 18},
        "Jacket": {"price": 2400, "stock": 8},
        "LED Headlight": {"price": 950, "stock": 12},
        "Air Filter": {"price": 300, "stock": 20},
        "Engine Oil": {"price": 600, "stock": 16},
        # Added Products
        "Disc Brake Oil": {"price": 320, "stock": 10},
        "Rear View Mirror": {"price": 250, "stock": 14},
        "Side Stand": {"price": 150, "stock": 20},
        "Clutch Wire": {"price": 100, "stock": 25},
        "Bike Cover": {"price": 550, "stock": 12}
    }
    save_data(inventory_file, default_inventory)

# --- App Class ---
class ShopBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🏍️ Shop Billing System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f4f7")

        style = ttk.Style()
        style.configure('TNotebook.Tab', padding=[10, 5], font=('Helvetica', 11, 'bold'))
        style.configure('TButton', font=('Helvetica', 10))

        self.cart = {}
        self.total = 0

        self.notebook = ttk.Notebook(root)
        self.billing_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.inventory_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.report_tab = tk.Frame(self.notebook, bg="#ffffff")
        self.customer_tab = tk.Frame(self.notebook, bg="#ffffff")

        self.notebook.add(self.billing_tab, text="Billing")
        self.notebook.add(self.inventory_tab, text="Inventory")
        self.notebook.add(self.report_tab, text="Reports")
        self.notebook.add(self.customer_tab, text="Customers")
        self.notebook.pack(expand=1, fill="both")

        self.setup_billing_tab()
        self.setup_inventory_tab()
        self.setup_report_tab()
        self.setup_customer_tab()

    # --- BILLING TAB ---
    def setup_billing_tab(self):
        self.inventory = load_data(inventory_file)
        frame = self.billing_tab

        tk.Label(frame, text="Customer Name:", bg="#ffffff", font=("Arial", 11)).grid(row=0, column=0, pady=5)
        tk.Label(frame, text="Phone:", bg="#ffffff", font=("Arial", 11)).grid(row=1, column=0, pady=5)
        self.name_entry = tk.Entry(frame, font=("Arial", 11))
        self.phone_entry = tk.Entry(frame, font=("Arial", 11))
        self.name_entry.grid(row=0, column=1, pady=5)
        self.phone_entry.grid(row=1, column=1, pady=5)

        self.item_listbox = tk.Listbox(frame, height=10, width=40, font=("Arial", 10))
        self.item_listbox.grid(row=2, column=0, columnspan=2, pady=10)
        self.update_item_list()

        tk.Label(frame, text="Quantity:", bg="#ffffff", font=("Arial", 11)).grid(row=3, column=0)
        self.qty_entry = tk.Entry(frame, font=("Arial", 11))
        self.qty_entry.grid(row=3, column=1)

        self.add_btn = tk.Button(frame, text="Add to Cart", command=self.add_to_cart, bg="#4caf50", fg="white", font=("Arial", 11, "bold"))
        self.add_btn.grid(row=4, column=0, columnspan=2, pady=10)

        self.cart_box = tk.Text(frame, height=10, width=50, font=("Courier New", 10))
        self.cart_box.grid(row=5, column=0, columnspan=2, pady=10)

        self.checkout_btn = tk.Button(frame, text="\ud83d\udcff Checkout", command=self.checkout, bg="#2196f3", fg="white", font=("Arial", 12, "bold"))
        self.checkout_btn.grid(row=6, column=0, columnspan=2, pady=10)

    def update_item_list(self):
        self.inventory = load_data(inventory_file)
        self.item_listbox.delete(0, tk.END)
        for item, info in self.inventory.items():
            self.item_listbox.insert(tk.END, f"{item} - ₹{info['price']} - Stock: {info['stock']}")

    def add_to_cart(self):
        selection = self.item_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a product.")
            return

        item_text = self.item_listbox.get(selection[0])
        item = item_text.split(" - ")[0]
        try:
            qty = int(self.qty_entry.get())
        except:
            messagebox.showerror("Error", "Invalid quantity.")
            return

        if qty > self.inventory[item]['stock']:
            messagebox.showerror("Error", "Stock not enough.")
            return

        self.cart[item] = self.cart.get(item, 0) + qty
        self.total += self.inventory[item]['price'] * qty
        self.inventory[item]['stock'] -= qty
        self.qty_entry.delete(0, tk.END)
        self.show_cart()
        self.update_item_list()

    def show_cart(self):
        self.cart_box.delete("1.0", tk.END)
        for item, qty in self.cart.items():
            price = self.inventory[item]['price']
            self.cart_box.insert(tk.END, f"{item} x{qty} = ₹{price * qty}\n")
        self.cart_box.insert(tk.END, f"\nTotal: ₹{self.total}")

    def checkout(self):
        try:
            if not self.cart:
                messagebox.showinfo("Empty", "Cart is empty.")
                return

            name = self.name_entry.get()
            phone = self.phone_entry.get()

            if not name or not phone:
                messagebox.showwarning("Input Required", "Enter customer details.")
                return

            gst = self.total * 0.05
            grand_total = self.total + gst

            customers = load_data(customers_file)
            customer = customers.get(phone, {"name": name, "points": 0, "history": []})
            sales = load_data(sales_file)

            discount = 0
            if customer['points'] >= 10:
                use = messagebox.askyesno("Discount", "Use 10 points for 10% discount?")
                if use:
                    discount = grand_total * 0.1
                    grand_total -= discount
                    customer['points'] -= 10

            points_earned = int(grand_total // 100)
            customer['points'] += points_earned
            tier = "Gold" if customer['points'] >= 50 else "Silver" if customer['points'] >= 25 else "Bronze"

            bill_no = f"SB{len(sales['sales']) + 1}"
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            bill_filename = f"Bill_{bill_no}.txt"
            with open(bill_filename, "w", encoding="utf-8") as f:
                f.write(f"Bill No: {bill_no}\nDate: {date_time}\n")
                for item, qty in self.cart.items():
                    price = self.inventory[item]['price']
                    f.write(f"{item} x{qty} = ₹{price * qty}\n")
                f.write(f"Subtotal: ₹{self.total:.2f}\nGST: ₹{gst:.2f}\n")
                if discount:
                    f.write(f"Discount: ₹{discount:.2f}\n")
                f.write(f"Total: ₹{grand_total:.2f}\nPoints: {customer['points']} ({tier})")

            customer['history'].append({
                "bill_no": bill_no, "date": date_time, "amount": grand_total
            })
            customers[phone] = customer
            sales['sales'].append({
                "bill_no": bill_no, "date": date_time, "amount": grand_total
            })
            sales['total_sales'] += grand_total

            save_data(inventory_file, self.inventory)
            save_data(customers_file, customers)
            save_data(sales_file, sales)

            messagebox.showinfo("Bill", f"Bill Generated\nTotal: ₹{grand_total:.2f}\nPoints: {customer['points']} ({tier})")

            self.cart.clear()
            self.total = 0
            self.name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.show_cart()
            self.update_item_list()

        except Exception as e:
            messagebox.showerror("Checkout Error", str(e))

    # --- INVENTORY TAB ---
    def setup_inventory_tab(self):
        frame = self.inventory_tab
        tk.Label(frame, text="Admin PIN:", bg="#ffffff", font=("Arial", 11)).grid(row=0, column=0, pady=5)
        self.pin_entry = tk.Entry(frame, show="*", font=("Arial", 11))
        self.pin_entry.grid(row=0, column=1, pady=5)
        tk.Button(frame, text="Unlock", command=self.unlock_admin, bg="#673ab7", fg="white").grid(row=0, column=2, pady=5)

        self.inv_text = tk.Text(frame, height=10, width=50, state="disabled", font=("Courier New", 10))
        self.inv_text.grid(row=1, column=0, columnspan=3, pady=10)

        tk.Label(frame, text="Item Name:", bg="#ffffff", font=("Arial", 11)).grid(row=2, column=0, pady=5)
        tk.Label(frame, text="Price:", bg="#ffffff", font=("Arial", 11)).grid(row=3, column=0, pady=5)
        tk.Label(frame, text="Stock:", bg="#ffffff", font=("Arial", 11)).grid(row=4, column=0, pady=5)

        self.item_entry = tk.Entry(frame, font=("Arial", 11))
        self.price_entry = tk.Entry(frame, font=("Arial", 11))
        self.stock_entry = tk.Entry(frame, font=("Arial", 11))
        self.item_entry.grid(row=2, column=1)
        self.price_entry.grid(row=3, column=1)
        self.stock_entry.grid(row=4, column=1)

        self.add_item_btn = tk.Button(frame, text="Add/Update Item", command=self.add_update_item, state="disabled", bg="#009688", fg="white")
        self.add_item_btn.grid(row=5, column=0, columnspan=3, pady=10)

    def unlock_admin(self):
        if self.pin_entry.get() == "22522":
            self.add_item_btn.config(state="normal")
            self.inv_text.config(state="normal")
            self.inv_text.delete("1.0", tk.END)
            inventory = load_data(inventory_file)
            for item, info in inventory.items():
                self.inv_text.insert(tk.END, f"{item}: ₹{info['price']} | Stock: {info['stock']}\n")
            self.inv_text.config(state="disabled")
        else:
            messagebox.showerror("Access Denied", "Incorrect PIN.")

    def add_update_item(self):
        item = self.item_entry.get().title()
        try:
            price = int(self.price_entry.get())
            stock = int(self.stock_entry.get())
        except:
            messagebox.showerror("Error", "Invalid price/stock.")
            return

        inventory = load_data(inventory_file)
        inventory[item] = {"price": price, "stock": stock}
        save_data(inventory_file, inventory)
        messagebox.showinfo("Updated", f"{item} added/updated.")
        self.unlock_admin()

    # --- REPORT TAB ---
    def setup_report_tab(self):
        frame = self.report_tab
        tk.Button(frame, text="View Total Sales", command=self.total_sales, bg="#03a9f4", fg="white").pack(pady=10)
        tk.Button(frame, text="Today's Sales Summary", command=self.today_sales, bg="#ff9800", fg="white").pack(pady=10)
        self.report_output = tk.Text(frame, height=15, width=60, font=("Courier New", 10))
        self.report_output.pack(pady=10)

    def total_sales(self):
        sales = load_data(sales_file)
        self.report_output.delete("1.0", tk.END)
        self.report_output.insert(tk.END, f"Total Sales: ₹{sales['total_sales']:.2f}\n")
        self.report_output.insert(tk.END, f"Total Bills: {len(sales['sales'])}")

    def today_sales(self):
        sales = load_data(sales_file)
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        today_sales = [s for s in sales['sales'] if today in s['date']]
        total = sum(s['amount'] for s in today_sales)
        self.report_output.delete("1.0", tk.END)
        self.report_output.insert(tk.END, f"Today's Sales: ₹{total:.2f} from {len(today_sales)} bills.")

    # --- CUSTOMER TAB ---
    def setup_customer_tab(self):
        frame = self.customer_tab

        tk.Label(frame, text="Enter Phone Number:", bg="#ffffff", font=("Arial", 11)).pack(pady=5)
        self.cust_phone_entry = tk.Entry(frame, font=("Arial", 11))
        self.cust_phone_entry.pack(pady=5)
        tk.Button(frame, text="Get Info", command=self.show_customer_info, bg="#009688", fg="white").pack(pady=5)

        self.customer_output = tk.Text(frame, height=15, width=60, font=("Courier New", 10))
        self.customer_output.pack(pady=10)

    def show_customer_info(self):
        phone = self.cust_phone_entry.get()
        customers = load_data(customers_file)
        self.customer_output.delete("1.0", tk.END)
        if phone in customers:
            cust = customers[phone]
            self.customer_output.insert(tk.END, f"Name: {cust['name']}\nPhone: {phone}\nPoints: {cust['points']}\n")
            self.customer_output.insert(tk.END, "\n--- Purchase History ---\n")
            for record in cust['history']:
                self.customer_output.insert(tk.END, f"Bill No: {record['bill_no']} | Date: {record['date']} | Amount: ₹{record['amount']:.2f}\n")
        else:
            self.customer_output.insert(tk.END, "Customer not found.")

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = ShopBillingApp(root)
    root.mainloop()
tk.tk