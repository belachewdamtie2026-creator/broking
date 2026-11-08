import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="የባህር ዳር ኦንላይን ድለላ", layout="wide")

# 🎨 የድረ-ገጹን መዋቅር ሳይነካ ኢንተርፌሱን ማራኪ ለማድረግ የተጨመረ ባለቀለም CSS ዲዛይን
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #f0f4f8 0%, #e2e8f0 100%);
        }
        .worker-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 20px;
            padding: 26px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
            border-left: 6px solid #3b82f6;
            margin-bottom: 30px;
        }
        .stImage > img {
            border-radius: 15px !important;
        }
        .stForm {
            background: #ffffff !important;
            border-radius: 20px !important;
            padding: 35px !important;
            border: 1px solid #cbd5e1 !important;
        }
    </style>
""", unsafe_allow_html=True)

def init_db():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS applicants (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, phone TEXT NOT NULL, job_type TEXT NOT NULL, experience TEXT, photo BLOB)')
    cursor.execute('CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, employer_name TEXT NOT NULL, employer_phone TEXT NOT NULL, applicant_id INTEGER, applicant_name TEXT, status TEXT DEFAULT "አዲስ ጥያቄ")')
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

def delete_applicant(applicant_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applicants WHERE id = ?', (applicant_id,))
    conn.commit()
    conn.close()

page = st.sidebar.radio("ምናሌ (Menu)", ["📝 የሰራተኛ መመዝገቢያ", "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር", "📊 Admin Only"])

st.title("💼 ፈጣን ድለላ")

if page == "📝 የሰራተኛ መመዝገቢያ":
    st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ:")
        uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("(ይመዝገቡ)")
        
        if submit_button and name and phone and uploaded_file:
            photo_bytes = uploaded_file.read()
            conn = sqlite3.connect('database.db', check_same_thread=False)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO applicants (name, phone, job_type, experience, photo) VALUES (?, ?, ?, ?, ?)', (name, phone, job_type, experience, photo_bytes))
            conn.commit()
            conn.close()
            st.success("🎉 ማመልከቻዎ በተሳካ ሁኔታ ደርሶናል!")

elif page == "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር":
    st.subheader("የሚፈልጉትን ሰራተኛ ይምረጡ")
    df = load_data()
    if not df.empty:
        job_filter = st.selectbox("የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        
        for index, row in filtered_df.iterrows():
            st.markdown('<div class="worker-card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                if row['photo']:
                    st.image(Image.open(io.BytesIO(row['photo'])), width=150, caption=f"ኮድ BDR-{row['id']}")
                else:
                    st.write("❌ ፎቶ የለም")
            with col2:
                badge_color = "#ea580c" if row['job_type'] == "የቡና አፍዪ" else ("#16a34a" if row['job_type'] == "ወጥ ቤት" else "#7c3aed")
                st.subheader(f"ስም: {row['name']}")
                st.markdown(f"<p style='font-size:16px;'>💼 <b>የስራ ዘርፍ:</b> <span style='background-color:{badge_color}; color:#ffffff; padding:4px 10px; border-radius:12px; font-weight:600;'>{row['job_type']}</span></p>", unsafe_allow_html=True)
                st.write(f"📜 **የስራ ልምድ:** {row['experience']}")
                
                show_form = st.checkbox(f"ይህንን ሰራተኛ መቅጠር እፈልጋለሁ", key=f"check_{row['id']}")
                if show_form:
                    with st.form(f"order_form_{row['id']}", clear_on_submit=True):
                        emp_name = st.text_input("የእርስዎ ስም:", key=f"emp_name_{row['id']}")
                        emp_phone = st.text_input("የእርስዎ ስልክ:", key=f"emp_phone_{row['id']}")
                        if st.form_submit_button("የቅጥር ጥያቄውን ላክ") and emp_name and emp_phone:
                            conn = sqlite3.connect('database.db', check_same_thread=False)
                            cursor = conn.cursor()
                            cursor.execute('INSERT INTO orders (employer_name, employer_phone, applicant_id, applicant_name) VALUES (?, ?, ?, ?)', (emp_name, emp_phone, row['id'], row['name']))
                            conn.commit()
                            conn.close()
                            st.success("🎉 የቅጥር ጥያቄዎ በተሳካ ሁኔታ ደርሶናል!")
            st.markdown('</div>', unsafe_allow_html=True)

elif page == "📊 Admin Only":
    st.subheader("🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ")
    password = st.text_input("Password ያስገቡ፦", type="password")
    if password == "bdr123":
        tab1, tab2 = st.tabs(["👥 የተመዘገቡ ሰራተኞች", "📥 የመጡ የቅጥር ጥያቄዎች"])
        with tab1:
            df = load_data()
            if not df.empty:
                for index, row in df.iterrows():
                    st.markdown('<div class="worker-card">', unsafe_allow_html=True)
                    admin_col1, admin_col2, admin_col3 = st.columns(3)
                    with admin_col1:
                        if row['photo']:
                            st.image(Image.open(io.BytesIO(row['photo'])), width=80)
                    with admin_col2:
                        st.markdown(f"**መለያ ቁጥር:** BDR-{row['id']} | **ስም:** {row['name']}\n\n📞 **ስልክ:** {row['phone']} | 💼 **ስራ:** {row['job_type']}")
                    with admin_col3:
                        if st.button(f"❌ አጥፋ", key=f"del_{row['id']}"):
                            delete_applicant(row['id'])
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
        with tab2:
            orders_df = load_orders()
            if not orders_df.empty:
                st.dataframe(orders_df, use_container_width=True)
                order_to_update = st.selectbox("የቅጥር ጥያቄ መለያ (ID) ይምረጡ፦", options=orders_df["id"].tolist())
                if st.button("ጥያቄውን እንደ 'ተጠናቋል' መዝግብ"):
                    update_order_status(order_to_update, "ተጠናቋል")
                    st.rerun()
