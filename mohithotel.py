import streamlit as st
import mysql.connector
from dbconfig import DB_CONFIG
from datetime import datetime
import re
import pandas as pd
import os
from PIL import Image
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_carousel import carousel



# ------------------ DATABASE FUNCTIONS ------------------

def init_db():
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS mohit2 (
            id INTEGER PRIMARY KEY AUTO_INCREMENT,
            name TEXT,
            mob TEXT,
            address TEXT,
            items TEXT,
            total FLOAT,
            datetime DATETIME,
            discount_percent FLOAT DEFAULT 0,
            discount_amount FLOAT DEFAULT 0          
        )
    """)
    conn.commit()
    conn.close()

def insert_order(name, mob, address, items, total, discount_percent, discount_amount):
    conn = mysql.connector.connect(**DB_CONFIG)
    c = conn.cursor()
    c.execute("""
        INSERT INTO mohit2 (name, mob, address, items, total, datetime, discount_percent, discount_amount)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        name,
        mob,
        address,
        items,
        total,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        discount_percent,
        discount_amount
    ))
    conn.commit()
    conn.close()


def get_order_count_by_mobile(mobile):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM mohit2 WHERE mob = %s", (mobile,))
    result = cursor.fetchone()
    count = result[0] if result else 0
    conn.close()
    return count




def get_orders():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, mob, address, items, total, datetime, discount_percent, discount_amount
        FROM mohit2
        ORDER BY id DESC
    """)
    fdata = cursor.fetchall()
    conn.close()
    return fdata


def get_latest_order(mob):
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, mob, address, items, total, datetime, discount_percent, discount_amount
        FROM mohit2
        WHERE mob = %s
        ORDER BY datetime DESC
        LIMIT 1
    """, (mob,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "name": row[1],
            "mob": row[2],
            "address": row[3],
            "items": row[4],
            "total": row[5],
            "datetime": row[6],
            "discount_percent": row[7],
            "discount_amount": row[8]
        }
    return None

# ------------------ INITIAL SETUP ------------------

init_db()

st.set_page_config(page_title="Restaurant App", layout="wide")

if "menu" not in st.session_state:
    st.session_state["menu"] = "Menu"


if "order_saved" not in st.session_state:
    st.session_state["order_saved"] = False

if "quantities" not in st.session_state:
    st.session_state.quantities = {}
if "cart" not in st.session_state:
    st.session_state.cart = {}

with st.sidebar:
    st.image("hologo.jpg", use_container_width=True)

    st.markdown("### 📋 Main Menu", unsafe_allow_html=True)

    menu_options = ["Menu", "Payment", "Confirm Payment", "My Order", "Admin"]
    selected_menu = st.radio("", menu_options, index=menu_options.index(st.session_state["menu"]))

    if st.session_state["menu"] != selected_menu:
        st.session_state["menu"] = selected_menu
        st.stop()

    st.markdown("---")

    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; font-size: 15px;">
        <h4 style='margin-bottom: 10px;'>🏨 <span style='color:#b22222'>DAGAR HOTEL</span></h4>
        📍 <b>Location:</b> Nuh road, Mandkola<br>
        📞 <b>Phone:</b> <a href="tel:+918168879243">+91-8168879243</a>, <a href="tel:+918295941711">8295941711</a><br>
        ⏰ <b>Timing:</b> 11 AM - 12 PM
    </div>
    """, unsafe_allow_html=True)




# -------------- HEADER --------------
restaurant_name = "🍽 DAGAR HOTEL 🍽"

# 🌟 Beautiful header with background and mobile padding
st.markdown(f"""
    <div style='
        background: linear-gradient(90deg, #ffe4e1 0%, #fff8dc 100%);
        padding: 30px 10px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        margin-bottom: 20px;
    '>
        <h1 style='color: #c0392b; font-size: 32px; margin-bottom: 10px;'>{restaurant_name}</h1>
        <p style='color: #555; font-size: 16px; font-weight: 500;'>
            Welcome to our restaurant — Authentic Indian Flavors
        </p>
    </div>
""", unsafe_allow_html=True)


# Your images list with required keys
slider_images = [
    {"img": "roti.jpg", "title": "Roti","text":"Roti"},
    {"img": "prntha.jpg", "title": "Paratha","text":"Roti"},
    {"img": "shipnr.jpg", "title": "Shipnr","text":"Roti"},
    {"img": "sahipnr_re.jpg", "title": "Sahipnr","text":"Roti"},
    {"img": "dahi.jpg", "title": "Dahi","text":"Roti"},
]
st.markdown("### 🍲 Popular Dishes")
# Display the carousel
carousel(slider_images)

# ------------------ MENU ------------------

images = {
    "Curry": "shipnr.jpg",
    "Roti": "roti.jpg",
    "Beverage": "coc.jpg"
}

menu = {
    "Curry": {
        "Matar Paneer(Half)": 70,
        "Matar Paneer(Full)": 130,
        "Kadhai Paneer(Half)": 100,
        "Kadhai Paneer(Full)": 180,
        "Mix Veg(Half)": 100,
        "Mix Veg(Full)": 180,
        "Shahi Paneer(Half)": 80,
        "Shahi Paneer(Full)": 150,
        "Butter Paneer Masala(Half)": 130,
        "Butter Paneer Masala(Full)": 230,
        "Paneer Bhurji(Half)": 180,
        "Paneer Bhurji(Full)": 300,
        "Matar Mushroom(Half)": 70,
        "Matar Mushroom(Full)": 130,
        "Sev Bhurji": 120,
        "Dal Makhani(Half)": 70,
        "Dal Makhani(Full)": 120,
        "Dal Tadka(Half)": 50,
        "Dal Tadka(Full)": 80,
        "Amritsari Chhole(Half)": 70,
        "Amritsari Chhole(Full)": 120,
        "Chana Masala": 180,
    },
    "Roti": {
        "Sadha Roti": 10,
        "Butter Roti": 15,
        "Pyaj Roti": 15,
        "Butter Pyaj Roti": 20,
        "Missi Roti": 20,
        "Butter Missi Roti": 25,
        "Garlic Nan": 25,
        "Butter Garlic Nan": 30,
        "Butter Nan": 30,
        "Sadha Nan": 20,
        "Aloo Nan": 30,
        "Butter Aloo Nan": 40,
        "Paneer Nan": 50,
        "Butter Paneer Nan": 60,
    },
    "Beverage": {
        "Raita": 50,
        "Dahi": 50,
        "Water Bottle": 20,
        "Cold drink": 50,
        "Mix Salad": 30,
        "Green Salad": 60,
    }
}

MIN_ORDER = 200  # minimum order amount in rupees

def increment(item):
    st.session_state.quantities[item] = st.session_state.quantities.get(item, 0) + 1

def decrement(item):
    if st.session_state.quantities.get(item, 0) > 0:
        st.session_state.quantities[item] -= 1

def add_all_to_cart_and_maybe_go_to_payment(navigate_on_success=True):
    """
    Add selected items from all categories to the cart,
    return the computed total.
    """
    # clear previous cart entries for items that may have been changed
    for category in menu:
        for item in menu[category].keys():
            # remove items with zero qty (if present)
            if item in st.session_state.cart and st.session_state.quantities.get(item, 0) == 0:
                del st.session_state.cart[item]

    # add/update items with qty > 0
    for category in menu:
        for item, price in menu[category].items():
            qty = st.session_state.quantities.get(item, 0)
            if qty > 0:
                st.session_state.cart[item] = {"qty": qty, "price": price}

    # compute total
    total = sum(info["qty"] * info["price"] for info in st.session_state.cart.values())

    if total < MIN_ORDER:
        needed = MIN_ORDER - total
        st.warning(f"Minimum order is ₹{MIN_ORDER}. Add ₹{needed} more to proceed.")
        return total, False

    st.success("✅ All selected items added to cart!")
    if navigate_on_success:
        st.session_state["menu"] = "Payment"
        # rerun so Payment page is displayed immediately
        st.stop()

    return total, True

def display_item(item, price):
    cols = st.columns([2, 6, 4])
    img = None
    for cat, items in menu.items():
        if item in items:
            img = images.get(cat)
            break
    with cols[0]:
        if img:
            st.image(img, width=60)
        else:
            st.write("🖼️")
    with cols[1]:
        st.markdown(f"**{item}**")
        st.markdown(f"₹{price}")
    with cols[2]:
        qty = st.session_state.quantities.get(item, 0)
        btn_cols = st.columns([1, 1, 1])
        with btn_cols[0]:
            if st.button("➖", key=f"dec_{item}"):
                decrement(item)
        with btn_cols[1]:
            st.markdown(f"<div style='text-align:center; font-size:20px;'>{qty}</div>", unsafe_allow_html=True)
        with btn_cols[2]:
            if st.button("➕", key=f"inc_{item}"):
                increment(item)

# ------------------ MENU PAGE ------------------
if st.session_state.get("menu", "Menu") == "Menu":
    st.title("📖 Menu Card")

    # Render all categories/items
    for category, items in menu.items():
        st.markdown(f"### {category} Items")
        for item, price in items.items():
            display_item(item, price)

    # Single add-all button (checks MIN_ORDER and navigates to Payment on success)
    if st.button("🛒 Add All Items to Cart"):
        add_all_to_cart_and_maybe_go_to_payment(navigate_on_success=True)

    # Cart summary (still useful to show on Menu page)
    st.markdown("---")
    st.subheader("🛒 Cart Summary")

    if not st.session_state.cart:
        st.write("Your cart is empty.")
    else:
        total = 0
        for item, info in st.session_state.cart.items():
            item_total = info["qty"] * info["price"]
            total += item_total
            st.write(f"{item} x {info['qty']} = ₹{item_total}")
        st.markdown(f"**Total: ₹{total}**")

        # optional: user can still go to Payment manually if they want
        if st.button("💳 Proceed to Payment"):
            # re-check minimum before navigating
            if total <= MIN_ORDER:
                st.warning(f"Minimum order is ₹{MIN_ORDER}. Please add more items.")
            else:
                st.session_state["menu"] = "Payment"
                st.stop()



# ------------------ PAYMENT ------------------

elif st.session_state.get("menu") == "Payment":
    st.subheader("💳 Payment Page")
    cart = st.session_state.get("cart", {})

    if not cart:
        st.warning("Your cart is empty. Please add items from the menu.")
        if st.button("Go to Menu"):
            st.session_state["menu"] = "Menu"
            st.stop()
    else:
        # Pre-fill fields if user_details already in session (user edited and returned)
        prev = st.session_state.get("user_details", {})
        name = st.text_input("Your Name", value=prev.get("name", ""))
        mob = st.text_input("Mobile Number", max_chars=10, value=prev.get("mob", ""))
        address = st.text_area("Delivery Address", value=prev.get("address", ""))

        # First calculate original total
        total = sum(info["qty"] * info["price"] for info in cart.values())

        # --- Discount Logic ---
        discount_percent = 0
        order_count = 0

        if re.match(r'^[6-9]\d{9}$', mob.strip()):
            
            order_count = get_order_count_by_mobile(mob.strip())

            if order_count == 0:
                discount_percent = 50
                st.success("🎉 First order! 50% discount applied.")
            elif order_count == 2:
                discount_percent = 30
                st.success("🎉 3rd order! 30% discount applied.")
            elif order_count == 9:
                discount_percent = 40
                st.success("🎉 10th order! 40% discount applied.")
            elif order_count >= 10:
                st.info("🧾 ")

        # Apply discount if applicable
        if discount_percent > 0:
            discount_amount = total * (discount_percent / 100)
            total -= discount_amount
            st.markdown(f"**Discount ({discount_percent}%): -₹{discount_amount:.2f}**")

        # Order Summary
        st.markdown("### Your Order Summary:")
        for item, details in cart.items():
            st.write(f"{item} x {details['qty']} = ₹{details['price'] * details['qty']}")
        st.markdown(f"### **Total to Pay: ₹{total:.2f}**")
        st.markdown("---")

        # Proceed to Confirm Payment (validate first)
        if st.button("➡️ Proceed to Confirm Payment"):
            if not name.strip():
                st.error("Please enter your name.")
            elif not re.match(r'^[6-9]\d{9}$', mob.strip()):
                st.error("Please enter a valid 10-digit Indian mobile number starting with 6-9.")
            elif not address.strip():
                st.error("Please enter delivery address.")
            else:
                # Save to session and go to confirm page
                st.session_state["user_details"] = {
                    "name": name.strip(),
                    "mob": mob.strip(),
                    "address": address.strip()
                }
                st.session_state["menu"] = "Confirm Payment"
                st.stop()

        # Allow going back to menu to change order
        if st.button("🔙 Back to Menu"):
            st.session_state["menu"] = "Menu"
            st.stop()



# ------------------ CONFIRM PAYMENT ------------------

elif st.session_state.get("menu") == "Confirm Payment":
    st.subheader("✅ Confirm Your Payment")

    # safety checks
    cart = st.session_state.get("cart", {})
    user_details = st.session_state.get("user_details")

    if not cart:
        st.warning("Your cart is empty. Please add items from the menu.")
        if st.button("Go to Menu"):
            st.session_state["menu"] = "Menu"
            st.stop()
        st.stop()

    if not user_details:
        st.warning("Please fill customer details on the Payment page first.")
        if st.button("Go to Payment"):
            st.session_state["menu"] = "Payment"
            st.stop()
        st.stop()

    # calculate total
    total = sum(info["qty"] * info["price"] for info in cart.values())

    # --- Discount Logic (Same as Payment Page) ---
    discount_percent = 0
    discount_amount = 0
    mob = user_details["mob"]

    if re.match(r'^[6-9]\d{9}$', mob.strip()):
          # or your actual function location
        order_count = get_order_count_by_mobile(mob.strip())

        if order_count == 0:
            discount_percent = 50
        elif order_count == 2:
            discount_percent = 30
        elif order_count == 9:
            discount_percent = 40

    if discount_percent > 0:
        discount_amount = total * (discount_percent / 100)
        total -= discount_amount

    # show order summary + customer details
    st.markdown("### 🛒 Order Summary")
    for item, info in cart.items():
        st.write(f"{item} x {info['qty']} = ₹{info['qty'] * info['price']}")
    if discount_percent > 0:
        st.markdown(f"**Discount ({discount_percent}%): -₹{discount_amount:.2f}**")
    st.markdown(f"**Total: ₹{total:.2f}**")

    st.markdown("---")
    st.markdown("### 🧑‍💼 Customer Details")
    st.write(f"**Name:** {user_details['name']}")
    st.write(f"**Mobile:** {user_details['mob']}")
    st.write(f"**Address:** {user_details['address']}")

    st.markdown("---")
    st.image("hoscan1.jpg", width=300)  # optional: your UPI image
    st.markdown("#### Please pay via UPI using the following ID:")
    st.markdown("`paytmqr51bzf8@ptys`")
    st.markdown("After completing the payment, click the button below.")

    if st.button("✅ Payment Done — I've Paid"):
        # Build items string
        items_str = ", ".join([f"{itm} x {inf['qty']}" for itm, inf in cart.items()])

        try:
            # Insert order into DB with discounted total
            insert_order(user_details["name"], user_details["mob"], user_details["address"], items_str, total, discount_percent, discount_amount)

        except Exception as e:
            st.error(f"Error saving order to DB: {e}")
            st.stop()

        st.success("🙏 Thank you! Your order has been placed successfully.")
        # cleanup
        st.session_state.pop("cart", None)
        st.session_state.pop("user_details", None)
        st.session_state["quantities"] = {}
        st.session_state["menu"] = "Menu"
        st.stop()

    if st.button("🔙 Go back to Payment"):
        st.session_state["menu"] = "Payment"
        st.stop()



elif st.session_state.get("menu") == "My Order":
    st.subheader("📋 My Latest Order")

    mob = st.text_input("Enter your registered mobile number:")

    if mob:
        latest_order = get_latest_order(mob)

        if latest_order:
            st.write(f"🧑‍💼 **Name:** {latest_order['name']}")
            st.write(f"📱 **Mobile:** {latest_order['mob']}")
            st.write(f"🏠 **Address:** {latest_order['address']}")
            st.write(f"🛒 **Items:** {latest_order['items']}")

            discount_amt = latest_order['discount_amount'] or 0
            st.write(f"💰 **Original Total:** ₹{latest_order['total'] + discount_amt:.2f}")


            st.write(f"🏷️ **Discount:** {latest_order.get('discount_percent', 0)}%")
            st.write(f"💸 **Discount Amount:** ₹{latest_order.get('discount_amount', 0):.2f}")

            # Show total after discount
            st.write(f"💰 **Total to Pay:** ₹{latest_order['total']:.2f}")

            st.write(f"📍 **DateTime:** {latest_order['datetime']}")
        else:
            st.info("No recent order found for this number.")
    else:
        st.warning("Please enter your mobile number.")


elif st.session_state.get("menu") == "Admin":
    st.subheader("🔑 Admin Login")

    admin_user = "admin"
    admin_pass = "1234"

    username = st.text_input("Username", placeholder="Enter username")
    password = st.text_input("Password", type="password", placeholder="Enter password")

    if st.button("Login"):
        if username == admin_user and password == admin_pass:
            st.success("✅ Logged in as Admin")

            orders = get_orders()
            if orders:
                import pandas as pd
                from st_aggrid import AgGrid, GridOptionsBuilder

                # Assuming orders include discount_percent and discount_amount in the tuple/list
                df = pd.DataFrame(orders, columns=[
                    "ID", "Name", "Mobile", "Address", "Items", "Total", "DateTime", "Discount Percent", "Discount Amount"
                ])

                # Format items with line breaks for readability
                df["Items"] = df["Items"].apply(lambda x: x.replace(", ", "\n"))

                # Format monetary columns to 2 decimals for neatness
                df["Total"] = df["Total"].map(lambda x: f"₹{x:.2f}")
                df["Discount Amount"] = df["Discount Amount"].map(lambda x: f"₹{x:.2f}")
                df["Discount Percent"] = df["Discount Percent"].map(lambda x: f"{x}%")

                # Grid options (NO filters/sorting)
                gb = GridOptionsBuilder.from_dataframe(df)
                gb.configure_default_column(
                    wrapText=True,
                    autoHeight=True,
                    resizable=True,
                    sortable=False,
                    filter=False
                )
                gb.configure_column("Items", wrapText=True, autoHeight=True)
                gb.configure_grid_options(domLayout='autoHeight')  # auto fit grid
                grid_options = gb.build()

                # Display Grid
                st.markdown("### 📋 All Orders (Mobile View)")
                AgGrid(
                    df,
                    gridOptions=grid_options,
                    theme="streamlit",  # Clean and soft theme
                    allow_unsafe_jscode=False,
                    fit_columns_on_grid_load=True,
                    height=500,
                    use_container_width=True
                )

                st.caption("👆 Scroll vertically to view all orders clearly.")
            else:
                st.info("No orders found.")
        else:
            st.error("❌ Invalid credentials")

    st.stop()

