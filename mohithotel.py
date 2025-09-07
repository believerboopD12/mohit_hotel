import streamlit as st
from datetime import datetime
import re
import os
from google.cloud import firestore
import pandas as pd


def init_db():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "mohitapikey.json"
    db = firestore.Client()
    return db


def save_order_to_firestore(db, name, mob, address, items, total):
    doc_ref = db.collection("orders").document()
    doc_id = doc_ref.id  
    doc_ref.set({
        "id": doc_id,
        "name": name,
        "mob": mob,
        "address": address,
        "items": items,
        "total": float(total),
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.success("Order saved successfully!")




def insert_order(db,order_data):
    doc_ref = db.collection("orders").document() 
    doc_ref.set(order_data)


def get_orders():
    
    orders_ref = db.collection("orders").order_by("datetime", direction="DESCENDING").stream()
    orders = []
    for doc in orders_ref:
        order_data = doc.to_dict()
        order_data["id"] = doc.id  
        orders.append(order_data)
    return orders



def get_latest_order(mob):
    
        
    results = db.collection("orders") \
        .where("mob", "==", mob) \
        .order_by("datetime", direction=firestore.Query.DESCENDING) \
        .limit(1) \
        .stream()

    for doc in results:
        return doc.to_dict()
    return None

    

st.set_page_config(page_title="Restaurant App", layout="wide")
db = init_db()  

col1, col2, col3 = st.columns([1, 3, 1])

with col1:
    st.image(r"hologo.jpg",width="stretch")

with col2:
    st.markdown("<h1 style='text-align: center; color: brown; font-size:50px;'>🍴 DAGAR HOTEL 🍴</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center;font-size:40px;text-decoration:underline;'>Welcome to our restaurant</h4>", unsafe_allow_html=True)

with col3:
    st.image(r"hologo.jpg",width="stretch")

st.markdown("---")

st.sidebar.image(r"fudlogo.jpg")


if "menu" not in st.session_state:
    st.session_state["menu"] = "Menu"


menu_options = ["Menu", "Payment","My Order", "Admin"]
if "user_details" in st.session_state:
    menu_options.insert(2, "Confirm Payment")


st.session_state["menu"] = st.sidebar.radio("Navigate", menu_options, index=menu_options.index(st.session_state["menu"]))


menu = st.session_state["menu"]




with st.sidebar.expander("ℹ️ About Us / Contact"):
    st.write("**🍴 DAGAR HOTEL**")
    st.write("📍 Location:Nuh road,Mandkola")
    st.write("📞 Phone:[+91-8168879243,8295941711]")
    
    st.write("⏰ Timing: 11 AM - 12 PM")




if menu == "Menu":
    st.subheader("📖 Menu Card")

   

    curry_items = {
        "Matar Paneer(Half)":70,
        "Matar Paneer(Full)":130,
        "Kadhai Paneer(Half)":100,
        "Kadhai Paneer(Full)": 180,
        "Mix Veg(Half)":100,
        "Mix Veg(Full)": 180,
        "Shahi Paneer(half)": 80,
        "Shahi Paneer(Full)":150,
        "Butter Paneer Masala(Half)": 130,
        "Butter Paneer Masala(Full)": 230,
        "Paneer Bhurji(Half)": 180,
        "Paneer Bhurji(Full)":300,
        "Matar Mushroom(Half)":70,
        "Matar Mushroom(Full)": 130,
        "Sev Bhurji":120,
        "Dal Makhani(Half)": 70,
        "Dal Makhani(Full)": 120,
        "Dal Tadka(Half)": 50,
        "Dal Tadka(Full)":80,
        "Amritsari Chhole(Half)": 70,
        "Amritsari Chhole(Full)":120,
        "Chana Masala": 180
    }

    roti_items = {
        "Sadha Roti":10,
        "Butter Roti":15,
        "Pyaj Roti": 15,
        "Butter Pyaj Roti": 20,
        "Missi Roti":20,
        "Butter Missi Roti": 25,
        "Garlic Nan":25,
        "Butter Garlic Nan": 30,
        "Butter Nan": 30,
        "Sadha Nan": 20,
        "Aloo Nan": 30,
        "Butter Aloo Nan": 40,
        "Paneer Nan": 50,
        "Butter Paneer Nan":60
    }

    beverage_items = {
        "Raita": 50,
        "Dahi": 50,
        "Water Bottle":20,
        "Cold drink":50,
        "Mix Salad":30,
        "Green Salad": 60
                }
    st.subheader("Select Items")
    selected_items = []
    total = 0

    def show_menu_section(title, items_dict):
        global total
        st.markdown(f"### {title}")
        for item, price in items_dict.items():
            qty = st.number_input(f"{item} (₹{price})", min_value=0, max_value=50, step=1, key=item)
            if qty > 0:
                selected_items.append(f"{item} x{qty}")
                total += price * qty

    
   
    
    col1, col2,col3 = st.columns(3)
    with col1:
        st.image("sahipnr_re.jpg", caption="Matar Mushroom")
    with col2:
        st.image("shipnr.jpg", caption="Sahi Paneer")
    with col3:
        st.image("dal.jpg", caption="Dal")

    show_menu_section("🍛 Curry Items", curry_items)

    st.markdown("----")
    col1, col2,col3 = st.columns(3)
    with col1:
        st.image("roti.jpg", caption="Sadha Roti")
    with col2:
        st.image("tndroti.jpg", caption="Tandoori Roti")
    with col3:
        st.image("prntha.jpg", caption="Parantha")

    show_menu_section("🍞 Roti Items", roti_items)

    st.markdown("----")
    col1, col2,col3 = st.columns(3)
    with col1:
        st.image("dahi.jpg", caption="Lassi")
    with col2:
        st.image("coc.jpg", caption="Cold drink")
    with col3:
        st.image("chai.jpg", caption="Tea")

    show_menu_section("🥤 Beverages", beverage_items)

    st.write(f"### 🧾 Total: ₹{total}")


    
    if total < 200:
        st.warning("⚠️ Minimum order amount is ₹200 to proceed to payment.")
        st.button("Proceed to Payment", disabled=True)
    else:
        if st.button("Proceed to Payment"):
                
            st.session_state["cart"] = {"items": selected_items, "total": total}
             
            st.session_state["menu"] = "Payment"
            st.stop()    
            



elif menu == "Payment":
    st.subheader("💳 Payment")
    if "order_saved" not in st.session_state:
        st.session_state["order_saved"] = False


    if "cart" not in st.session_state:
        st.warning("No items selected. Please go to Menu first.")
    else:
        cart = st.session_state["cart"]
        st.write("### Items Ordered")
        st.write(", ".join(cart["items"]))
        st.write(f"### Total: ₹{cart['total']}")

        st.subheader("Enter Your Details")
        name = st.text_input("Name")
        mob = st.text_input("Mobile")
        address = st.text_area("Address")

        if st.button("Pay & Place Order"):

            if st.session_state.get("order_saved", False):
                st.warning("⚠️ Order already placed. Proceed to payment.")
                st.session_state["menu"] = "Confirm Payment"
                st.stop()

            elif not re.match(r'^[6-9]\d{9}$', mob):
                st.warning("⚠️ Invalid mobile number.")
            else:
                
                if name and mob and address:
                    order_data = {
                        "name": name,
                        "mob": mob,
                        "address": address,
                        "items": ", ".join(cart["items"]),
                        "total": cart["total"],
                        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    insert_order(db, order_data)

                    st.success("✅ Order details saved. Please proceed to payment.")

                    st.session_state["order_saved"] = True
                    st.session_state["user_details"] = {
                        "name": name,
                        "mob": mob,
                        "address": address,
                    }

                    st.session_state["menu"] = "Confirm Payment"
                    st.stop()


            st.balloons()


elif menu == "Confirm Payment":
    st.subheader("✅ Confirm Your Payment")
    st.balloons()

    
    if "cart" not in st.session_state or "user_details" not in st.session_state:
        st.warning("Please complete the payment form first.")
        st.stop()

    st.image("hoscan1.jpg", width=300)
    st.markdown("----")
    st.markdown("**UPI ID:** `paytmqr51bzf8@ptys`")
    st.markdown("---")
    

    if st.button("✅ Done"):
        st.balloons()
        st.success("Thank you for your order.Please wait 30 mins and keep a solid proof of payment")

        
        st.session_state.pop("cart", None)
        st.session_state.pop("user_details", None)

        
        st.session_state["menu"] = "Menu"
        st.stop()

elif menu == "My Order":
    st.subheader("📋 My Latest Order")

    if "user_details" in st.session_state and "mob" in st.session_state["user_details"]:
        mob = st.session_state["user_details"]["mob"]

    else:  
        mob = st.text_input("Please enter your mobile number to see your latest order:")

        
    if mob:
        st.session_state["user_details"] = {"mob": mob }      
        latest_order = get_latest_order(mob)
        if latest_order:
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"👤 **Name:** {latest_order.get('name', 'N/A')}")
                st.markdown(f"📱 **Mobile:** {latest_order.get('mob', 'N/A')}")
                st.markdown(f"🏠 **Address:** {latest_order.get('address', 'N/A')}")

            with col2:
                items = latest_order.get('items', 'N/A')
                if isinstance(items, list):
                    items_display = "\n".join(f"- {item}" for item in items)
                elif isinstance(items, str):
                    items_list = [item.strip() for item in items.split(',')]
                    items_display = "\n".join(f"- {item}" for item in items_list)
                else:
                    items_display = str(items)


                st.markdown(f"🛒 **Items:** {latest_order.get('items', 'N/A')}")
                st.markdown(f"💰 **Total:** ₹{latest_order.get('total', 'N/A')}")
                st.markdown(f"⏰ **DateTime:** {latest_order.get('datetime', 'N/A')}")
                st.balloons()
        else:
            st.info("No recent order found.")

    else:
        st.info("Enter your mobile number above to view your latest order.")



elif menu == "Admin":
    st.subheader("🔑 Admin Login")

    admin_user = "admin"
    admin_pass = "1234"

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == admin_user and password == admin_pass:
            st.success("✅ Logged in as Admin")
            st.balloons()
            orders = get_orders()
            if orders:
                st.subheader("📋 All Orders")
               
                df = pd.DataFrame(orders)
                df = df.drop(columns=['id'])
                df.index = df.index + 1
              
                def format_items_markdown(items_str):
                
                    items_list = [item.strip() for item in items_str.split(',')]
                    
                    return "<br>".join(items_list)

                df['items'] = df['items'].apply(format_items_markdown)
                st.write(df.to_html(escape=False), unsafe_allow_html=True)


                


            else:
                st.info("No orders yet.")
        else:
            st.error("❌ Invalid credentials")

        st.session_state["menu"] = "Menu"
        st.stop()