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

# የጎን ምናሌ (Menu)
page = st.sidebar.radio("ምናሌ (Menu)", [
    "📝 የሰራተኛ መመዝገቢያ ቅፅ", 
    "🏨 የሰራተኞች ማሳያ (ለቀጣሪዎች)", 
    "📊 የአስተዳዳሪ ሰሌዳ (Admin Only)"
])

# ----- ገፅ 1፦ የሰራተኛ መመዝገቢያ ቅፅ -----
if page == "📝 የሰራተኛ መመዝገቢያ ቅፅ":
    st.title("የሰራተኛ መመዝገቢያ")
    st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
    st.markdown("---")
    
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም (ለምሳሌ፡ አልማዝ አበበ):")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ (ምሳሌ፡ 2 አመት በሆቴል):")
        uploaded_file = st.file_uploader("ፎቶዎን እዚህ ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("አፕላይ አድርግ (ይመዝገቡ)")
        
        if submit_button:
            if name and phone and uploaded_file:
                photo_bytes = uploaded_file.read()
                conn = sqlite3.connect('database.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO applicants (name, phone, job_type, experience, photo) VALUES (?, ?, ?, ?, ?)',
                               (name, phone, job_type, experience, photo_bytes))
                conn.commit()
                conn.close()
                st.success("🎉 ማመልከቻዎ እና ፎቶዎ በተሳካ ሁኔታ ደርሶናል! በቅርቡ እንገናኛለን።")
            else:
                st.error("እባክዎ ስም፣ ስልክ እና ፎቶ በትክክል ያስገቡ!")

# ----- ገፅ 2፦ የሰራተኞች ማሳያ (ለቀጣሪዎች) -----
elif page == "🏨 የሰራተኞች ማሳያ (ለቀጣሪዎች)":
    st.title("ዝግጁ የሆኑ ሰራተኞች ዝርዝር")
    st.subheader("የሚፈልጉትን ሰራተኛ ይምረጡ")
    st.markdown("---")
    
    df = load_data()
    
    if not df.empty:
        job_filter = st.selectbox("የሚፈልጉትን የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns()
            
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
                                st.success("🎉 የቅጥር ጥያቄዎ በተሳካ ሁኔታ ለአስተዳዳሪው ደርሷል! በቅጽበት በስልክዎ እንገናኛለን።")
                            else:
                                st.error("እባክዎ ስምዎትንና ስልክ ቁጥርዎን ያስገቡ!")
            st.markdown("---")
    else:
        st.info("ለጊዜው የተመዘገበ ሰራተኛ የለም።")

# ----- ገፅ 3፦ የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ (Admin) -----
elif page == "📊 የአስተዳዳሪ ሰሌዳ (Admin Only)":
    st.title("🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ")
    st.markdown("---")
    
    password = st.text_input("የአስተዳዳሪ ሚስጥራዊ ቁጥር (Password) ያስገቡ፦", type="password")
    
    if password == "bdr123":
        tab1, tab2 = st.tabs(["👥 የተመዘገቡ ሰራተኞች", "📥 የመጡ የቅጥር ጥያቄዎች (Orders)"])
        
        with tab1:
            st.subheader("የተመዘገቡ ሰራተኞች ሙሉ መረጃ")
            df = load_data()
            if not df.empty:
                st.dataframe(df[["id", "name", "phone", "job_type", "experience"]], use_container_width=True)
            else:
                st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
                
        with tab2:
            st.subheader("📥 ከቀጣሪዎች የመጡ የቅጥር ጥያቄዎች ዝርዝር")
            orders_df = load_orders()
            if not orders_df.empty:
                st.dataframe(orders_df[["id", "employer_name", "employer_phone", "applicant_id", "applicant_name", "status"]], use_container_width=True)
            else:
                st.info("እስካሁን ምንም የቀጥር ጥያቄ አልመጣም።")
                
    elif password != "":
        st.error("የገቡት ሚስጥራዊ ቁጥር የተሳሳተ ነው!")
