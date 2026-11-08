import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

# የገፅ ቅንጅት እና ለዓይን ማራኪ እንዲሆን የተደረገ የ CSS ዲዛይን
st.set_page_config(page_title="ፈጣን ድለላ - ባህር ዳር", layout="wide")

st.markdown("""
    <style>
        /* ጠቅላላ የበስተጀርባ ቀለም */
        .stApp {
            background-color: #f8f9fa;
        }
        
        /* የዋናው ርዕስ ውበት */
        .main-title {
            font-size: 38px !important;
            font-weight: 800 !important;
            color: #1E3A8A !important;
            text-align: center;
            margin-bottom: 5px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .sub-title {
            font-size: 18px !important;
            color: #6B7280 !important;
            text-align: center;
            margin-bottom: 30px;
        }
        
        /* ከላይ ያሉ ታቦች (Tabs) ውበት */
        .stTabs [data-baseweb="tab-list"] {
            gap: 15px;
            justify-content: center;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: #ffffff;
            border: 1px solid #E5E7EB;
            padding: 12px 24px !important;
            border-radius: 30px !important;
            font-weight: 600 !important;
            color: #4B5563 !important;
            transition: all 0.3s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: #1E3A8A !important;
            border-color: #1E3A8A;
            background-color: #EFF6FF;
        }
        .stTabs [aria-selected="true"] {
            background-color: #1E3A8A !important;
            color: #ffffff !important;
            border-color: #1E3A8A !important;
        }
        
        /* የሰራተኞች ካርድ (Card Design) ውበት */
        .worker-card {
            background-color: #ffffff;
            border-radius: 16px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #F3F4F6;
            margin-bottom: 25px;
            transition: transform 0.2s ease;
        }
        .worker-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        }
        
        /* የፎቶዎች አቀማመጥ */
        .worker-img {
            border-radius: 12px !important;
            object-fit: cover;
            border: 3px solid #EFF6FF;
        }
        
        /* ፎርሞች እና ሳጥኖች */
        .stForm {
            background-color: #ffffff !important;
            border-radius: 16px !important;
            padding: 30px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            border: 1px solid #E5E7EB !important;
        }
    </style>
""", unsafe_allow_html=True)

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

def delete_applicant(applicant_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM applicants WHERE id = ?', (applicant_id,))
    conn.commit()
    conn.close()

# ማራኪ ዋና አርዕስት
st.markdown('<div class="main-title">💼 ፈጣን ድለላ</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">የባህር ዳር ዘመናዊ የሰራተኛ እና ቀጣሪ ማገናኛ መድረክ</div>', unsafe_allow_html=True)

main_tab1, main_tab2, main_tab3 = st.tabs([
    "📝 የሰራተኛ መመዝገቢያ", 
    "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር", 
    "📊 Admin Only"
])

# ----- ገፅ 1፦ የሰራተኛ መመዝገቢያ -----
with main_tab1:
    st.markdown("<h3 style='color:#1E3A8A; font-weight:600;'>የሰራተኛ መመዝገቢያ ቅፅ</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;'>መረጃዎን በትክክል በመሙላት በፍጥነት ስራ ያግኙ</p>", unsafe_allow_html=True)
    
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ (ምሳሌ፦ 2 አመት በሆቴል):")
        uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
        
        submit_button = st.form_submit_button("ለመመዝገብ እዚህ ይጫኑ 🚀")
        
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
                st.error("እባክዎ ሁሉንም መረጃዎች እና ፎቶዎን በትክክል ያስገቡ!")

# ----- ገፅ 2፦ ዝግጁ የሆኑ ሰራተኞች ዝርዝር -----
with main_tab2:
    st.markdown("<h3 style='color:#1E3A8A; font-weight:600;'>በስራ ዝግጁ የሆኑ ሰራተኞች</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280;'>የሚፈልጉትን ሰራተኛ በሙያ መርጠው የቅጥር ጥያቄ መላክ ይችላሉ</p>", unsafe_allow_html=True)
    
    df = load_data()
    
    if not df.empty:
        job_filter = st.selectbox("የስራ አይነት በመምረጥ ያጣሩ፦", ["ሁሉም"] + list(df["job_type"].unique()))
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        
        st.markdown("---")
        
        for index, row in filtered_df.iterrows():
            st.markdown('<div class="worker-card">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            
            with col1:
                if row['photo']:
                    image = Image.open(io.BytesIO(row['photo']))
                    st.image(image, width=160, caption=f"ኮድ፡ BDR-{row['id']}")
                else:
                    st.image("https://placeholder.com", width=160, caption="ፎቶ የለም")
                    
            with col2:
                st.markdown(f"<h3 style='color:#1E3A8A; margin-top:0;'>ስም: {row['name']}</h3>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:16px;'>💼 <b>የስራ ዘርፍ:</b> <span style='background-color:#EFF6FF; color:#1E3A8A; padding:4px 10px; border-radius:12px; font-weight:600;'>{row['job_type']}</span></p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size:16px; color:#4B5563;'>📜 <b>የስራ ልምድ:</b> {row['experience']}</p>", unsafe_allow_html=True)
                
                show_form = st.checkbox(f"ይህንን ሰራተኛ መቅጠር እፈልጋለሁ (ኮድ: BDR-{row['id']})", key=f"check_{row['id']}")
                
                if show_form:
                    st.markdown("<br>", unsafe_allow_html=True)
                    with st.form(f"order_form_{row['id']}", clear_on_submit=True):
                        emp_name = st.text_input("የእርስዎ ስም (የቀጣሪው ስም):", key=f"emp_name_{row['id']}")
                        emp_phone = st.text_input("የእርስዎ ስልክ ቁጥር (ለመገናኘት):", key=f"emp_phone_{row['id']}")
                        submit_order = st.form_submit_button("የቅጥር ጥያቄውን በቅጽበት ላክ 📩")
                        
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
                                st.success("🎉 የቅጥር ጥያቄዎ በተሳካ ሁኔታ ደርሶናል! በአጭር ጊዜ ውስጥ በስልክ እንገናኛለን።")
                            else:
                                st.error("እባክዎ ስምዎን እና ስልክ ቁጥርዎን ያስገቡ!")
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("ለጊዜው የተመዘገበ ሰራተኛ የለም።")

# ----- ገፅ 3፦ Admin Only -----
with main_tab3:
    st.markdown("<h3 style='color:#1E3A8A; font-weight:600;'>🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ</h3>", unsafe_allow_html=True)
    
    password = st.text_input("የአስተዳዳሪ ሚስጥራዊ ቁጥር (Password) ያስገቡ፦", type="password", key="admin_password_direct")
    
    if password == "bdr123":
        admin_sub_tab1, admin_sub_tab2 = st.tabs(["👥 የተመዘገቡ ሰራተኞች", "📥 የመጡ የቅጥር ጥያቄዎች (Orders)"])
        
        with admin_sub_tab1:
            st.subheader("የተመዘገቡ ሰራተኞች ሙሉ መረጃ እና ፎቶ")
            df = load_data()
            if not df.empty:
