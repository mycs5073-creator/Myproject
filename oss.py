import tkinter as tk
from tkinter import messagebox

#--------------------
# Create account
#--------------------

def create_account():
    messagebox.showinfo("Create Account", "Account creation is not implemented in this demo.")
    
    

def login():
    if username.get() == "admin" and password.get() == "1234":
        messagebox.showinfo("Success", "Login Successful!")
        open_main_menu()
    else:
        messagebox.showerror("Error", "Invalid credentials")

root = tk.Tk()
root.title("Attendance Management System - Login")
root.geometry("300x200")

tk.Label(root, text="Username").pack(pady=5)
username = tk.Entry(root)
username.pack()

tk.Label(root, text="Password").pack(pady=5)
password = tk.Entry(root, show="*")
password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)
root.mainloop()

# ============================================================
# PRODUCT DATA
# ============================================================

products = [
    ("Laptop", 50000, "💻"),
    ("Mobile", 20000, "📱"),
    ("Apple", 10000, "🍎"),
    ("Headphones", 2000, "🎧"),
    ("Smart Watch", 3000, "⌚"),
    ("Keyboard", 1500, "⌨️"),
    ("Mouse", 800, "🖱️"),
    ("Monitor", 12000, "🖥️"),
    ("Tablet", 25000, "📱"),
]

# cart is keyed by product name -> {"price": int, "qty": int, "icon": str}
cart = {}


# ============================================================
# COLORS
# ============================================================

BG_COLOR = "#EAF2F8"
HEADER_COLOR = "#1F4E78"
CARD_COLOR = "#FFFFFF"
CARD_BORDER = "#D6E4EF"
BUTTON_COLOR = "#2874A6"
BUTTON_HOVER = "#1A5276"
TEXT_COLOR = "#17202A"
PRICE_COLOR = "#229954"
DANGER_COLOR = "#C0392B"
DANGER_HOVER = "#922B21"
MUTED_COLOR = "#5D6D7E"
MUTED_HOVER = "#455263"
ACCENT_COLOR = "#27AE60"
ACCENT_HOVER = "#1E8449"

CARD_WIDTH = 240
CARD_HEIGHT = 210
COLUMNS = 4


# ============================================================
# BUTTON HOVER EFFECT
# ============================================================

def button_hover(button, normal_color, hover_color):
    button.bind("<Enter>", lambda event: button.config(bg=hover_color))
    button.bind("<Leave>", lambda event: button.config(bg=normal_color))


# ============================================================
# MOUSEWHEEL SCROLL HELPER
# ============================================================

def bind_mousewheel(canvas, widget):
    def _on_mousewheel(event):
        delta = 0
        if event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        elif event.delta:
            delta = -1 if event.delta > 0 else 1
        canvas.yview_scroll(delta, "units")

    widget.bind("<Enter>", lambda e: (
        widget.bind_all("<MouseWheel>", _on_mousewheel),
        widget.bind_all("<Button-4>", _on_mousewheel),
        widget.bind_all("<Button-5>", _on_mousewheel),
    ))
    widget.bind("<Leave>", lambda e: (
        widget.unbind_all("<MouseWheel>"),
        widget.unbind_all("<Button-4>"),
        widget.unbind_all("<Button-5>"),
    ))


# ============================================================
# ADD PRODUCT TO CART
# ============================================================

def add_to_cart(name, price, icon):
    if name in cart:
        cart[name]["qty"] += 1
    else:
        cart[name] = {"price": price, "qty": 1, "icon": icon}

    update_cart_badge()

    messagebox.showinfo(
        "Shopping Cart",
        f"{name} added to cart successfully!"
    )


def update_cart_badge():
    total_items = sum(item["qty"] for item in cart.values())
    cart_button.config(text=f"🛒 VIEW CART  ({total_items})")


# ============================================================
# CREATE PRODUCT CARD
# ============================================================

def create_product_card(parent, name, price, icon, row, col):
    card = tk.Frame(
        parent,
        bg=CARD_COLOR,
        highlightbackground=CARD_BORDER,
        highlightthickness=1,
        bd=0,
        width=CARD_WIDTH,
        height=CARD_HEIGHT,
    )
    card.grid(row=row, column=col, padx=12, pady=12)
    card.grid_propagate(False)

    tk.Label(
        card, text=icon, font=("Arial", 40), bg=CARD_COLOR
    ).pack(pady=(18, 4))

    tk.Label(
        card, text=name, font=("Arial", 14, "bold"),
        bg=CARD_COLOR, fg=TEXT_COLOR
    ).pack()

    tk.Label(
        card, text=f"₹{price:,}", font=("Arial", 13, "bold"),
        bg=CARD_COLOR, fg=PRICE_COLOR
    ).pack(pady=(2, 8))

    add_button = tk.Button(
        card,
        text="Add to Cart",
        font=("Arial", 10, "bold"),
        bg=BUTTON_COLOR,
        fg="white",
        activebackground=BUTTON_HOVER,
        activeforeground="white",
        relief="flat",
        cursor="hand2",
        command=lambda: add_to_cart(name, price, icon),
    )
    add_button.pack(ipadx=6, ipady=4)

    button_hover(add_button, BUTTON_COLOR, BUTTON_HOVER)


# ============================================================
# RENDER A LIST OF PRODUCTS INTO THE GRID
# ============================================================

def render_products(product_list):
    for widget in product_frame.winfo_children():
        widget.destroy()

    if not product_list:
        tk.Label(
            product_frame,
            text="❌ No product found!",
            font=("Arial", 18, "bold"),
            bg=BG_COLOR,
            fg=DANGER_COLOR,
        ).grid(row=0, column=0, pady=60, padx=20)
        return

    for index, (name, price, icon) in enumerate(product_list):
        row = index // COLUMNS
        col = index % COLUMNS
        create_product_card(product_frame, name, price, icon, row, col)

    # Refresh the scroll region after the new content is drawn
    product_frame.update_idletasks()
    product_canvas.configure(scrollregion=product_canvas.bbox("all"))
    product_canvas.yview_moveto(0)


def show_all_products():
    search_entry.delete(0, tk.END)
    render_products(products)


def search_products():
    search_text = search_entry.get().strip().lower()

    if search_text == "":
        show_all_products()
        return

    results = [p for p in products if search_text in p[0].lower()]
    render_products(results)


# ============================================================
# CART OPERATIONS
# ============================================================

def change_quantity(name, delta, refresh_callback):
    if name not in cart:
        return

    cart[name]["qty"] += delta

    if cart[name]["qty"] <= 0:
        del cart[name]

    update_cart_badge()
    refresh_callback()


def clear_cart(cart_window):
    if not cart:
        return

    if messagebox.askyesno("Clear Cart", "Remove all items from the cart?"):
        cart.clear()
        update_cart_badge()
        cart_window.destroy()
        show_cart()


def place_order(cart_window):
    if not cart:
        messagebox.showwarning("Empty Cart", "Your shopping cart is empty!")
        return

    total = sum(item["price"] * item["qty"] for item in cart.values())

    result = messagebox.askyesno(
        "Confirm Order",
        f"Total Amount: ₹{total:,}\n\nDo you want to place this order?",
    )

    if result:
        cart.clear()
        update_cart_badge()
        messagebox.showinfo(
            "Order Successful",
            "🎉 Order placed successfully!\n\nThank you for shopping with us!",
        )
        cart_window.destroy()


# ============================================================
# SHOW SHOPPING CART
# ============================================================

def show_cart():
    cart_window = tk.Toplevel(root)
    cart_window.title("Shopping Cart")
    cart_window.geometry("650x650")
    cart_window.configure(bg=BG_COLOR)
    cart_window.resizable(False, False)
    cart_window.transient(root)
    cart_window.grab_set()

    # Header
    tk.Label(
        cart_window,
        text="🛒 MY SHOPPING CART",
        font=("Arial", 20, "bold"),
        bg=HEADER_COLOR,
        fg="white",
        pady=15,
    ).pack(fill="x")

    # Empty cart
    if not cart:
        tk.Label(
            cart_window,
            text="Your cart is empty!",
            font=("Arial", 16, "bold"),
            bg=BG_COLOR,
            fg=DANGER_COLOR,
        ).pack(pady=80)

        close_button = tk.Button(
            cart_window,
            text="Close",
            width=20,
            bg=BUTTON_COLOR,
            fg="white",
            font=("Arial", 11, "bold"),
            relief="flat",
            cursor="hand2",
            command=cart_window.destroy,
        )
        close_button.pack()
        button_hover(close_button, BUTTON_COLOR, BUTTON_HOVER)
        return

    # Scrollable items area
    outer_frame = tk.Frame(cart_window, bg=BG_COLOR)
    outer_frame.pack(fill="both", expand=True, padx=20, pady=(15, 5))

    cart_canvas = tk.Canvas(outer_frame, bg=BG_COLOR, highlightthickness=0)
    scrollbar = tk.Scrollbar(outer_frame, orient="vertical", command=cart_canvas.yview)
    items_frame = tk.Frame(cart_canvas, bg=BG_COLOR)

    items_frame.bind(
        "<Configure>",
        lambda e: cart_canvas.configure(scrollregion=cart_canvas.bbox("all")),
    )

    cart_canvas.create_window((0, 0), window=items_frame, anchor="nw")
    cart_canvas.configure(yscrollcommand=scrollbar.set)

    cart_canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    bind_mousewheel(cart_canvas, cart_canvas)

    total = 0

    for name, data in cart.items():
        price = data["price"]
        qty = data["qty"]
        icon = data["icon"]
        subtotal = price * qty
        total += subtotal

        item_frame = tk.Frame(
            items_frame,
            bg=CARD_COLOR,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
            padx=12,
            pady=10,
        )
        item_frame.pack(fill="x", pady=6)

        tk.Label(
            item_frame, text=icon, font=("Arial", 20), bg=CARD_COLOR
        ).grid(row=0, column=0, rowspan=2, padx=(0, 10))

        tk.Label(
            item_frame, text=name, font=("Arial", 13, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR
        ).grid(row=0, column=1, sticky="w")

        tk.Label(
            item_frame, text=f"₹{price:,} each", font=("Arial", 10),
            bg=CARD_COLOR, fg=MUTED_COLOR
        ).grid(row=1, column=1, sticky="w")

        # Quantity controls
        qty_frame = tk.Frame(item_frame, bg=CARD_COLOR)
        qty_frame.grid(row=0, column=2, rowspan=2, padx=15)

        minus_btn = tk.Button(
            qty_frame, text="−", width=2, bg=MUTED_COLOR, fg="white",
            relief="flat", font=("Arial", 10, "bold"), cursor="hand2",
            command=lambda n=name: (change_quantity(n, -1, lambda: (cart_window.destroy(), show_cart())))
        )
        minus_btn.grid(row=0, column=0)

        tk.Label(
            qty_frame, text=str(qty), font=("Arial", 12, "bold"),
            bg=CARD_COLOR, fg=TEXT_COLOR, width=3
        ).grid(row=0, column=1)

        plus_btn = tk.Button(
            qty_frame, text="+", width=2, bg=MUTED_COLOR, fg="white",
            relief="flat", font=("Arial", 10, "bold"), cursor="hand2",
            command=lambda n=name: (change_quantity(n, 1, lambda: (cart_window.destroy(), show_cart())))
        )
        plus_btn.grid(row=0, column=2)

        tk.Label(
            item_frame, text=f"₹{subtotal:,}", font=("Arial", 12, "bold"),
            bg=CARD_COLOR, fg=PRICE_COLOR, width=10, anchor="e"
        ).grid(row=0, column=3, rowspan=2)

        remove_button = tk.Button(
            item_frame, text="Remove", bg=DANGER_COLOR, fg="white",
            font=("Arial", 9, "bold"), relief="flat", cursor="hand2",
            command=lambda n=name: (
                cart.pop(n, None),
                update_cart_badge(),
                cart_window.destroy(),
                show_cart(),
            )
        )
        remove_button.grid(row=0, column=4, rowspan=2, padx=(15, 0))
        button_hover(remove_button, DANGER_COLOR, DANGER_HOVER)

    # Footer: total + actions
    footer = tk.Frame(cart_window, bg=BG_COLOR)
    footer.pack(fill="x", padx=20, pady=10)

    tk.Label(
        footer, text=f"TOTAL: ₹{total:,}", font=("Arial", 18, "bold"),
        bg=BG_COLOR, fg=PRICE_COLOR
    ).pack(pady=(0, 10))

    button_row = tk.Frame(footer, bg=BG_COLOR)
    button_row.pack()

    order_button = tk.Button(
        button_row, text="💳 PLACE ORDER", width=18, height=2,
        bg=ACCENT_COLOR, fg="white", font=("Arial", 11, "bold"),
        relief="flat", cursor="hand2",
        command=lambda: place_order(cart_window),
    )
    order_button.grid(row=0, column=0, padx=5)
    button_hover(order_button, ACCENT_COLOR, ACCENT_HOVER)

    clear_button = tk.Button(
        button_row, text="🗑 Clear Cart", width=14, height=2,
        bg=DANGER_COLOR, fg="white", font=("Arial", 11, "bold"),
        relief="flat", cursor="hand2",
        command=lambda: clear_cart(cart_window),
    )
    clear_button.grid(row=0, column=1, padx=5)
    button_hover(clear_button, DANGER_COLOR, DANGER_HOVER)

    close_button = tk.Button(
        button_row, text="Close", width=12, height=2,
        bg=MUTED_COLOR, fg="white", font=("Arial", 11, "bold"),
        relief="flat", cursor="hand2", command=cart_window.destroy,
    )
    close_button.grid(row=0, column=2, padx=5)
    button_hover(close_button, MUTED_COLOR, MUTED_HOVER)


# ============================================================
# MAIN WINDOW
# ============================================================

root = tk.Tk()
root.title("Online Shopping System")
root.geometry("1080x760")
root.minsize(900, 600)
root.configure(bg=BG_COLOR)


# ============================================================
# HEADER
# ============================================================

header = tk.Frame(root, bg=HEADER_COLOR, height=90)
header.pack(fill="x")
header.pack_propagate(False)

tk.Label(
    header,
    text="🛒 ONLINE SHOPPING SYSTEM",
    font=("Arial", 26, "bold"),
    bg=HEADER_COLOR,
    fg="white",
).pack(pady=20)


# ============================================================
# SEARCH SECTION
# ============================================================

search_frame = tk.Frame(root, bg=BG_COLOR)
search_frame.pack(pady=18)

search_entry = tk.Entry(
    search_frame, width=40, font=("Arial", 13), relief="solid", bd=1
)
search_entry.pack(side="left", padx=5, ipady=7)
search_entry.bind("<Return>", lambda e: search_products())

search_button = tk.Button(
    search_frame, text="🔍 Search", width=12, height=1,
    bg=BUTTON_COLOR, fg="white", font=("Arial", 10, "bold"),
    relief="flat", cursor="hand2", command=search_products,
)
search_button.pack(side="left", padx=5, ipady=6)
button_hover(search_button, BUTTON_COLOR, BUTTON_HOVER)

all_button = tk.Button(
    search_frame, text="Show All", width=12, height=1,
    bg=MUTED_COLOR, fg="white", font=("Arial", 10, "bold"),
    relief="flat", cursor="hand2", command=show_all_products,
)
all_button.pack(side="left", padx=5, ipady=6)
button_hover(all_button, MUTED_COLOR, MUTED_HOVER)


# ============================================================
# PRODUCT SECTION (SCROLLABLE GRID)
# ============================================================

tk.Label(
    root, text="Available Products", font=("Arial", 18, "bold"),
    bg=BG_COLOR, fg=TEXT_COLOR,
).pack(pady=(5, 0))

products_outer = tk.Frame(root, bg=BG_COLOR)
products_outer.pack(fill="both", expand=True, padx=20, pady=10)

product_canvas = tk.Canvas(products_outer, bg=BG_COLOR, highlightthickness=0)
product_scrollbar = tk.Scrollbar(
    products_outer, orient="vertical", command=product_canvas.yview
)
product_frame = tk.Frame(product_canvas, bg=BG_COLOR)

product_frame.bind(
    "<Configure>",
    lambda e: product_canvas.configure(scrollregion=product_canvas.bbox("all")),
)

product_canvas.create_window((0, 0), window=product_frame, anchor="nw")
product_canvas.configure(yscrollcommand=product_scrollbar.set)

product_canvas.pack(side="left", fill="both", expand=True)
product_scrollbar.pack(side="right", fill="y")
bind_mousewheel(product_canvas, product_canvas)

# Display products
show_all_products()


# ============================================================
# VIEW CART BUTTON
# ============================================================

cart_button = tk.Button(
    root, text="🛒 VIEW CART", width=30, height=2,
    bg=ACCENT_COLOR, fg="white", font=("Arial", 13, "bold"),
    relief="flat", cursor="hand2", command=show_cart,
)
cart_button.pack(pady=15)
button_hover(cart_button, ACCENT_COLOR, ACCENT_HOVER)


# ============================================================
# FOOTER
# ============================================================

tk.Label(
    root,
    text="Online Shopping System | Developed using Python & Tkinter",
    font=("Arial", 10),
    bg=BG_COLOR,
    fg=MUTED_COLOR,
).pack(side="bottom", pady=8)


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":
    root.mainloop()