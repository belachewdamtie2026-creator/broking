import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="የባህር ዳር ኦንላይን ድለላ", layout="wide")

# የዳታቤዝ መጀመሪያ ዝግጅት
def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applicants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            job_type TEXT NOT NULL,
            experience TEXT,
            photo BLOB
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_name TEXT NOT NULL,
            employer_phone TEXT NOT NULL,
            applicant_id INTEGER,
            applicant_name TEXT,
            status TEXT DEFAULT 'አዲስ ጥያቄ'
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM applicants", conn)
    conn.close()
    return df

def load_orders():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM orders", conn)
    conn.close()
    return df

def update_order_status(order_id, new_status):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()
    conn.close()

# ሰራተኛን ከዳታቤዝ ሙሉ በሙሉ ለማጥፋት የተጨመረ አዲስ ፈንክሽን
def delete_applicant(applicant_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applicants WHERE id = ?', (applicant_id,))
    conn.commit()
    conn.close()

# የጎን ምናሌ (Menu)
page = st.sidebar.radio("ምናሌ (Menu)", [
    "📝 የሰራተኛ መመዝገቢያ", 
    "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር", 
    "📊 Admin Only"
])

# ----- ገፅ 1፦ የሰራተኛ መመዝገቢያ -----
if page == "📝 የሰራተኛ መመዝገቢያ":
    st.title("የሰራተኛ መመዝገቢያ")
    st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
    st.markdown("---")
    
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ:")
        uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("(ይመዝገቡ)")
        
        if submit_button:
            if name and phone and uploaded_file:
                photo_bytes = uploaded_file.read()
                conn = sqlite3.connect('database.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO applicants (name, phone, job_type, experience, photo) VALUES (?, ?, ?, ?, ?)',
                               (name, phone, job_type, experience, photo_bytes))
                conn.commit()
                conn.close()
                st.success("🎉 ማመልከቻዎ በተሳካ ሁኔታ ደርሶናል! በቅርቡ እናሳውቅዎታለን።")
            else:
                st.error("እባክዎ ሁሉንም በትክክል ያስገቡ!")

# ----- ገፅ 2፦ ዝግጁ የሆኑ ሰራተኞች ዝርዝር -----
elif page == "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር":
    st.title("ዝግጁ የሆኑ ሰራተኞች ዝርዝር")
    st.subheader("የሚፈልጉትን ሰራተኛ ይምረጡ")
    st.markdown("---")
    
    df = load_data()
    
    if not df.empty:
        job_filter = st.selectbox("የሚፈልጉትን የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns(2)
            
            with col1:
                if row['photo']:
                    image = Image.open(io.BytesIO(row['photo']))
                    st.image(image, width=150, caption=f"ኮድ፡ BDR-{row['id']}")
                else:
                    st.image("https://placeholder.com", width=150, caption="ፎቶ የለም")
                    
            with col2:
                st.subheader(f"ስም: {row['name']}")
                st.write(f"💼 **የስራ ዘርፍ:** {row['job_type']}")
                st.write(f"📜 **የስራ ልምድ:** {row['experience']}")
                
                show_form = st.checkbox(f"ይህንን ሰራተኛ መቅጠር እፈልጋለሁ (ኮድ: BDR-{row['id']})", key=f"check_{row['id']}")
                
                if show_form:
                    with st.form(f"order_form_{row['id']}", clear_on_submit=True):
                        emp_name = st.text_input("የእርስዎ ስም (የቀጣሪው ስም):", key=f"emp_name_{row['id']}")
                        emp_phone = st.text_input("የእርስዎ ስልክ ቁጥር (ለመገናኘት):", key=f"emp_phone_{row['id']}")
                        submit_order = st.form_submit_button("የቅጥር ጥያቄውን ላክ")
                        
                        if submit_order:
                            if emp_name and emp_phone:
                                conn = sqlite3.connect('database.db', check_same_thread=False)
                                cursor = conn.cursor()
                                cursor.execute('''
                                    INSERT INTO orders (employer_name, employer_phone, applicant_id, applicant_name)
                                    VALUES (?, ?, ?, ?)
                                ''', (emp_name, emp_phone, row['id'], row['name']))
                                conn.commit()
                                conn.close()
                                st.success("🎉 የቅጥር ጥያቄዎ በተሳካ ሁኔታ ደርሶናል! በቅርቡ እናሳዉቅዎታለን።")
                            else:
                                st.error("እባክዎ ስምዎትንና ስልክ ቁጥርዎን ያስገቡ!")
            st.markdown("---")
    else:
        st.info("ለጊዜው የተመዘገበ ሰራተኛ የለም።")

# ----- ገፅ 3፦ Admin Only -----
elif page == "📊 Admin Only":
    st.title("🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ")
    st.markdown("---")
    
    password = st.text_input("የአስተዳዳሪ ሚስጥራዊ ቁጥር (Password) ያስገቡ፦", type="password")
    
    if password == "bdr123":
        tab1, tab2 = st.tabs(["👥 የተመዘገቡ ሰራተኞች", "📥 የመጡ የቅጥር ጥያቄዎች (Orders)"])
        
        with tab1:
            st.subheader("የተመዘገቡ ሰራተኞች ሙሉ መረጃ እና ፎቶ")
            df = load_data()
            if not df.empty:
                for index, row in df.iterrows():
                    admin_col1, admin_col2, admin_col3 = st.columns([1, 3, 1.5]) # የማጥፊያ ቁልፍ ለማስቀመጫ 3ኛ ኮለምን ተጨምሯል
                    
                    with admin_col1:
                        if row['photo']:
                            img = Image.open(io.BytesIO(row['photo']))
                            st.image(img, width=80)
                        else:
                            st.write("❌ ፎቶ የለም")
                            
                    with admin_col2:
                        st.markdown(f"**መለያ ቁጥር:** BDR-{row['id']} | **ስም:** {row['name']}")
                        st.markdown(f"📞 **ስልክ:** {row['phone']} | 💼 **ስራ:** {row['job_type']} | 📜 **ልምድ:** {row['experience']}")
                        
                    with admin_col3:
                        # በእያንዳንዱ ሰራተኛ መስመር ላይ የሚመጣ የማጥፊያ በተን
                        if st.button(f"❌ ሰራተኛውን አጥፋ", key=f"del_{row['id']}"):
                            delete_applicant(row['id'])
                            st.success(f"ሰራተኛ ቁጥር BDR-{row['id']} ከዝርዝር ጠፍቷል!")
                            st.rerun() # ገጹን በቅጽበት ለማደስ
                            
                    st.markdown("---")
            else:
                st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
                
        with tab2:
            st.subheader("📥 ከቀጣሪዎች የመጡ የቅጥር ጥያቄዎች ዝርዝር")
            orders_df = load_orders()
            if not orders_df.empty:
                st.dataframe(orders_df[["id", "employer_name", "employer_phone", "applicant_id", "applicant_name", "status"]], use_container_width=True)
                
                st.markdown("### የጥያቄ ሁኔታ ማዘመኛ")
                order_to_update = st.selectbox("የቅጥር ጥያቄ መለያ (ID) ይምረጡ፦", options=orders_df["id"].tolist())
                if st.button("ጥያቄውን እንደ 'ተጠናቋል' መዝግብ"):
                    update_order_status(order_to_update, "ተጠናቋል")
                    st.success(f"የጥያቄ ቁጥር {order_to_update} ሁኔታ በተሳካ ሁኔታ ታድሷል!")
                    st.rerun()
            else:
                st.info("እስካሁን ምንም ጥያቄ አልመጣም።")
                
    elif password != "":
        st.error("ሚስጥራዊ ቁጥር የተሳሳተ ነው!")
