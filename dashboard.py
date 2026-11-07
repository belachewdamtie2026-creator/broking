import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="የባህር ዳር ኦንላይን ድለላ", layout="wide", initial_sidebar_state="expanded")

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
            experience TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ዳታን ለማንበብ
def load_data():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM applicants", conn)
    conn.close()
    return df

# በጎን በኩል የሚመጣው ማውጫ (Navigation)
page = st.sidebar.radio("ምናሌ (Menu)", ["የሰራተኛ መመዝገቢያ ቅፅ", "የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ (Admin)"])

# ----- ገፅ 1፦ የሰራተኛ መመዝገቢያ ቅፅ -----
if page == "የሰራተኛ መመዝገቢያ ቅፅ":
    st.title("📝 የባህር ዳር ኦንላይን ድለላ - የሰራተኛ መመዝገቢያ")
    st.subheader("ከቤትዎ ሆነው መረጃዎን በቀላሉ ይመዝግቡ")
    st.markdown("---")
    
    with st.form("registration_form", clear_on_submit=True):
        name = st.text_input("ሙሉ ስም (ለምሳሌ፡ አልማዝ አበበ):")
        phone = st.text_input("ስልክ ቁጥር:")
        job_type = st.selectbox("የስራ አይነት:", ["የቡና አፍዪ", "ወጥ ቤት", "ፅዳት", "ሌላ"])
        experience = st.text_input("የስራ ልምድ (ምሳሌ፡ 2 አመት በሆቴል):")
        
        submit_button = st.form_submit_button("አፕላይ አድርግ (ይመዝገቡ)")
        
        if submit_button:
            if name and phone:
                conn = sqlite3.connect('database.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO applicants (name, phone, job_type, experience) VALUES (?, ?, ?, ?)',
                               (name, phone, job_type, experience))
                conn.commit()
                conn.close()
                st.success("🎉 ማመልከቻዎ በተሳካ ሁኔታ ደርሶናል! በቅርቡ እንገናኛለን።")
            else:
                st.error("እባክዎ ስም እና ስልክ ቁጥር በትክክል ያስገቡ!")

# ----- ገፅ 2፦ የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ -----
elif page == "የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ (Admin)":
    st.title("📊 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ")
    st.subheader("በድረ-ገጹ ላይ የተመዘገቡ ሰራተኞች ዝርዝር")
    st.markdown("---")
    
    df = load_data()
    
    if not df.empty:
        # የፍለጋ ማጣሪያዎች
        job_filter = st.multiselect(
            "በስራ አይነት ማጣሪያ (Filter):",
            options=df["job_type"].unique(),
            default=df["job_type"].unique()
        )
        
        filtered_df = df[df["job_type"].isin(job_filter)]
        
        st.metric(label="ጠቅላላ የተመዘገቡ ሰራተኞች ብዛት", value=len(filtered_df))
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
