import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="የባህር ዳር ኦንላይን ድለላ", layout="wide")

# 🎨 📱 ስልክ ላይ ጥቁር የነበሩትን ፎርሞች፣ የፎቶ መጫኛ (File Uploader) እና መምረጫዎች ሁልጊዜ ነጭ ለማድረግ የተደረገ CSS ማሻሻያ
st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #fef08a 0%, #f1f5f9 100%); }
        [data-testid="stHeader"] { background-color: #ffffff !important; }
        [data-testid="stHeader"] *, [data-testid="stHeader"] svg { color: #1e293b !important; fill: #1e293b !important; }
        html, body, [data-testid="stWidgetLabel"] p, .stMarkdown p, p, li, span {
            font-size: 22px !important; font-weight: 500 !important; color: #1e293b !important;
        }
        [data-testid="stFileUploader"] div, [data-testid="stFileUploaderDropzone"] {
            background-color: #ffffff !important; color: #1e293b !important; border: 2px dashed #cbd5e1 !important;
        }
        [data-testid="stFileUploaderDropzone"] p, [data-testid="stFileUploaderDropzone"] span { color: #1e293b !important; }
        div[data-testid="stTextInput"] input, div[data-testid="stNumberInput"] input {
            background-color: #ffffff !important; color: #1e293b !important; border: 1px solid #cbd5e1 !important;
        }
        [data-testid="stDataFrame"] div, [data-testid="stDataFrame"] table, [data-testid="stDataFrame"] th, [data-testid="stDataFrame"] td {
            background-color: #ffffff !important; color: #1e293b !important;
        }
        [data-testid="stSidebar"] { background-color: #ffffff !important; background: #ffffff !important; }
        [data-testid="stSidebar"] .stRadio label p { color: #1e293b !important; font-size: 18px !important; font-weight: 700 !important; }
        div[data-baseweb="select"] > div { background-color: #ffffff !important; color: #1e293b !important; border: 1px solid #cbd5e1 !important; }
        div[data-baseweb="popover"] ul, div[data-baseweb="popover"] li { background-color: #ffffff !important; color: #1e293b !important; }
        .stTabs [data-baseweb="tab"] p { color: #1e3a8a !important; font-size: 21px !important; font-weight: bold !important; }
        .stTabs [aria-selected="true"] p { color: #ffffff !important; }
        .worker-card {
            background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
            border-radius: 20px; padding: 26px; box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.05);
            border-left: 6px solid #3b82f6; margin-bottom: 30px;
        }
        div[data-testid="stCheckbox"] {
            background-color: #f0fdf4 !important; padding: 14px 24px !important; border-radius: 12px !important;
            border: 2px solid #22c55e !important; box-shadow: 0 4px 6px rgba(34, 197, 94, 0.15) !important;
            margin: 15px 0 !important; width: fit-content !important;
        }
        div[data-testid="stCheckbox"] label p { font-size: 21px !important; font-weight: 800 !important; color: #15803d !important; }
        input, select, textarea { font-size: 22px !important; color: #1e293b !important; background-color: #ffffff !important; }
        .stForm { background: #ffffff !important; border-radius: 20px !important; padding: 35px !important; border: 1px solid #cbd5e1 !important; }
        .stImage > img { border-radius: 15px !important; }
        div.stFormSubmitButton > button, div.stButton > button[key^="submit_"] {
            background-color: #16a34a !important; color: white !important; border-radius: 12px !important;
            border: none !important; padding: 14px 32px !important; font-weight: 800 !important; font-size: 20px !important;
        }
        div.stButton > button[key^="del_"], div.stButton > button[key^="delorder_"] { background-color: #dc2626 !important; color: white !important; font-size: 16px !important; }
        div.stButton > button:not([key^="del_"]):not([key^="delorder_"]):not([key^="submit_"]):not([data-testid="baseButton-secondaryFormSubmit"]) { background-color: #2563eb !important; color: white !important; }

        /* 🔠 ትልቅ የጽሁፍ መጠኖች */
        h1, h1 * { font-size: 42px !important; font-weight: 800 !important; color: #1e3a8a !important; }
        h2, h2 *, h3, h3 * { font-size: 30px !important; font-weight: 700 !important; color: #1e293b !important; }
        [data-testid="stWidgetLabel"] p { font-size: 23px !important; font-weight: 700 !important; }
        div[role="radiogroup"] label p { font-size: 22px !important; font-weight: 700 !important; }
        div[data-baseweb="select"] * { font-size: 22px !important; }
        div[data-baseweb="popover"] li, div[data-baseweb="popover"] li * { font-size: 22px !important; }
        div.stButton > button p, div.stFormSubmitButton > button p { font-size: 22px !important; font-weight: 800 !important; }
        [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { font-size: 20px !important; }
        [data-testid="stAlert"] p { font-size: 22px !important; }
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

def delete_order(order_id):
    conn = sqlite3.connect('database.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
    conn.commit()
    conn.close()

st.title("💼 ፈጣን ድለላ")

# menu
page = st.radio("ምናሌ (Menu)", ["📝 የሰራተኛ መመዝገቢያ", "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር", "📊 Admin Only"], horizontal=True)
 
if page == "📝 የሰራተኛ መመዝገቢያ":
    st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ:")
        uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
        submit_button = st.form_submit_button("ለመመዝገብ እዚህ ይጫኑ 🚀")
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
                        submit_order = st.form_submit_button("የቅጥር ጥያቄውን በቅጽበት ላክ 📩")
                        if submit_order and emp_name and emp_phone:
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
            df_admin = load_data()
            if not df_admin.empty:
                for index, row in df_admin.iterrows():
                    st.markdown('<div class="worker-card">', unsafe_allow_html=True)
                    st.markdown(f"**BDR-{row['id']}** | **ስም:** {row['name']} | 📞 **ስልክ:** {row['phone']} | 💼 **ስራ:** {row['job_type']}")
                    if st.button("❌ ይህንን ሰራተኛ አጥፋ", key=f"del_{row['id']}"):
                        delete_applicant(row['id'])
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else: st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
        with tab2:
            orders_df = load_orders()
            if not orders_df.empty:
                status_options = ["አዲስ ጥያቄ", "በሂደት ላይ", "ተጠናቋል"]
                for index, row in orders_df.iterrows():
                    order_id = int(row['id'])
                    st.markdown('<div class="worker-card">', unsafe_allow_html=True)
                    st.markdown(f"**ጥያቄ #{order_id}** | 🏢 **ቀጣሪ:** {row['employer_name']} | 📞 **ስልክ:** {row['employer_phone']}")
                    st.markdown(f"👤 **የተጠየቀው ሰራተኛ:** {row['applicant_name']} (BDR-{row['applicant_id']})")
                    st.markdown(f"📌 **አሁን ያለበት ሁኔታ:** {row['status']}")
                    current_status = row['status'] if row['status'] in status_options else status_options[0]
                    new_status = st.selectbox("ሁኔታ ቀይር:", status_options, index=status_options.index(current_status), key=f"status_{order_id}")
                    col_save, col_del = st.columns(2)
                    with col_save:
                        if st.button("💾 ሁኔታውን አስቀምጥ", key=f"save_{order_id}"):
                            update_order_status(order_id, new_status)
                            st.rerun()
                    with col_del:
                        if st.button("❌ ጥያቄውን አጥፋ", key=f"delorder_{order_id}"):
                            delete_order(order_id)
                            st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("እስካሁን ምንም የቅጥር ጥያቄ አልመጣም።")
    elif password:
        st.error("❌ Password የተሳሳተ ነው።")
