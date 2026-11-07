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
            salary INTEGER DEFAULT 3000,
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
    
    try:
        cursor.execute("ALTER TABLE applicants ADD COLUMN salary INTEGER DEFAULT 3000")
    except sqlite3.OperationalError:
        pass
        
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

# 🚀 ዋና ማሻሻያ፦ የአድሚን መግቢያ በግራ በኩል (Sidebar) ለብቻው ተደርጓል
st.sidebar.title("🔐 የአድሚን መግቢያ")
is_admin = st.sidebar.checkbox("የአስተዳዳሪ ገፅን ክፈት (Admin Option)")

# 1. የአስተዳዳሪ ገፅ ከተመረጠ (አድሚኑ በግራ በኩል ሲያበራው)
if is_admin:
    st.title("🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ (Admin)")
    st.markdown("---")
    
    password = st.sidebar.text_input("የአስተዳዳሪ ሚስጥራዊ ቁጥር ያስገቡ፦", type="password", key="admin_password_input")
    
    if password == "bdr123":
        tab1, tab2 = st.tabs(["👥 የተመዘገቡ ሰራተኞች", "📥 የመጡ የቅጥር ጥያቄዎች (Orders)"])
        
        with tab1:
            st.subheader("የተመዘገቡ ሰራተኞች ሙሉ መረጃ እና ፎቶ")
            df = load_data()
            if not df.empty:
                for index, row in df.iterrows():
                    admin_col1, admin_col2, admin_col3 = st.columns([1, 4, 1])
                    
                    with admin_col1:
                        if row['photo']:
                            img = Image.open(io.BytesIO(row['photo']))
                            st.image(img, width=80)
                        else:
                            st.write("❌ ፎቶ የለም")
                            
                    with admin_col2:
                        st.markdown(f"**መለያ ቁጥር:** BDR-{row['id']} | **ስም:** {row['name']}")
                        st.markdown(f"📞 **ስልክ:** {row['phone']} | 💼 **ስራ:** {row['job_type']} | 📜 **ልምድ:** {row['experience']} | 💰 **ደሞዝ:** {row['salary']} ብር")
                        
                    with admin_col3:
                        if st.button(f"❌ አጥፋ", key=f"del_{row['id']}"):
                            delete_applicant(row['id'])
                            st.success(f"ሰራተኛ ቁጥር BDR-{row['id']} ከዝርዝር ጠፍቷል!")
                            st.rerun()
                            
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
        st.sidebar.error("ሚስጥራዊ ቁጥር የተሳሳተ ነው!")
    else:
        st.info("እባክዎ በግራ በኩል ባለው ሳጥን ውስጥ የአስተዳዳሪ የይለፍ ቃልዎን ያስገቡ።")

# 2. መደበኛው የተጠቃሚዎች ገፅ (አድሚን ካልተመረጠ በቀጥታ የሚከፈተው)
else:
    st.title("🌟 የባህር ዳር ዲጂታል ድለላ")
    main_tab1, main_tab2 = st.tabs([
        "📝 የሰራተኛ መመዝገቢያ", 
        "🏨 ዝግጁ የሆኑ ሰራተኞች ዝርዝር"
    ])

    # ----- ገፅ 1፦ የሰራተኛ መመዝገቢያ -----
    with main_tab1:
        st.subheader("ከቤትዎ ሆነው በቀላሉ ይመዝግቡ")
        st.markdown("---")
        
        with st.form("registration_form", clear_on_submit=True):
            name = st.text_input("ሙሉ ስም")
            phone = st.text_input("ስልክ ቁጥር:")
            job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
            experience = st.text_input("የስራ ልምድ:")
            salary = st.number_input("የሚፈልጉት የወር ደሞዝ (በብር):", min_value=0, step=500, value=3000)
            uploaded_file = st.file_uploader("ፎቶዎን ይጫኑ (የግዴታ):", type=["jpg", "jpeg", "png"])
            
            submit_button = st.form_submit_button("(ይመዝገቡ)")
            
            if submit_button:
                if name and phone and uploaded_file:
                    photo_bytes = uploaded_file.read()
                    conn = sqlite3.connect('database.db', check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute('INSERT INTO applicants (name, phone, job_type, experience, salary, photo) VALUES (?, ?, ?, ?, ?, ?)',
                                   (name, phone, job_type, experience, salary, photo_bytes))
                    conn.commit()
                    conn.close()
                    st.success("🎉 ማመልከቻዎ እና ፎቶዎ በተሳካ ሁኔታ ደርሶናል! በቅርቡ እናሳውቅዎታለን።")
                else:
                    st.error("እባክዎ ሁሉንም በትክክል ያስገቡ!")

    # ----- ገፅ 2፦ ዝግጁ የሆኑ ሰራተኞች ዝርዝር -----
    with main_tab2:
        st.subheader("የሚፈልጉትን ሰራተኛ ይምረጡ")
        st.markdown("---")
        
        df = load_data()
        
        if not df.empty:
            filter_col1, filter_col2 = st.columns(2)
            with filter_col1:
                job_filter = st.selectbox("የሚፈልጉትን የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
            with filter_col2:
                max_salary = st.slider("ከፍተኛው የወር ደሞዝ ገደብ (በብር):", 
                                       min_value=int(df["salary"].min()), 
                                       max_value=int(df["salary"].max() + 1000), 
                                       value=int(df["salary"].max() + 1000))
            
            filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
            filtered_df = filtered_df[filtered_df["salary"] <= max_salary]
            
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
                    st.write(f"💰 **የሚፈልጉት ደሞዝ:** {row['salary']} ብር")
                    
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
