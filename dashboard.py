import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import io

st.set_page_config(page_title="የባህር ዳር ኦንላይን ድለላ", layout="wide")

# የዳታቤዝ መጀመሪያ ዝግጅት (ፎቶ እንዲቀበል BLOB ተጨምሯል)
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
    conn.commit()
    conn.close()

init_db()

def load_data():
    conn = sqlite3.connect('database.db', check_same_thread=False)
    df = pd.read_sql_query("SELECT * FROM applicants", conn)
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
    st.title("📝 የባህር ዳር ኦንላይን ድለላ - የሰራተኛ መመዝገቢያ")
    st.subheader("ከቤትዎ ሆነው መረጃዎን እና ፎቶዎን በቀላሉ ይመዝግቡ")
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
                # ፎቶውን ወደ ባይት (Bytes) መቀየር
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
    st.title("🏨 በስራ ዝግጁ የሆኑ ሰራተኞች ዝርዝር")
    st.subheader("የሚፈልጉትን ሰራተኛ በሙያ እና በፎቶ መርጠው ይቅጠሩ")
    st.info("💡 የምትፈልጉትን ሰራተኛ ሲያገኙ 'ይህንን ቅጠሩ' የሚለውን በመጫን እኛን ማግኘት ይችላሉ። (ለደህንነት ሲባል የሰራተኞች ስልክ ቁጥር አልተገለጸም)")
    st.markdown("---")
    
    df = load_data()
    
    if not df.empty:
        # የፍለጋ ማጣሪያ
        job_filter = st.selectbox("የሚፈልጉትን የስራ አይነት ይምረጡ:", ["ሁሉም"] + list(df["job_type"].unique()))
        
        filtered_df = df if job_filter == "ሁሉም" else df[df["job_type"] == job_filter]
        
        # ሰራተኞችን በካርድ መልክ (በየተራ) ማሳየት
        for index, row in filtered_df.iterrows():
            col1, col2 = st.columns([1, 3])
            
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
                if st.button(f"ይህንን ቅጠሩ (ኮድ: BDR-{row['id']})", key=row['id']):
                    st.success(f"📩 ጥያቄዎ ተመዝግቧል! ስለ ሰራተኛ 'BDR-{row['id']}' ለማገናኘት በስልክ መስመራችን 09XXXXXXXX ይደውሉልን።")
            st.markdown("---")
    else:
        st.info("ለጊዜው የተመዘገበ ሰরাተኛ የለም።")

# ----- ገፅ 3፦ የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ (Admin) -----
elif page == "📊 የአስተዳዳሪ ሰሌዳ (Admin Only)":
    st.title("🔒 የአስተዳዳሪ መቆጣጠሪያ ሰሌዳ")
    st.subheader("የተመዘገቡ ሰራተኞች ሙሉ መረጃ ከስልክ ቁጥር ጋር")
    st.markdown("---")
    
    password = st.text_input("የአስተዳዳሪ ሚስጥራዊ ቁጥር (Password) ያስገቡ፦", type="password")
    
    if password == "bdr123": # ሚስጥራዊ ቁጥሩን እዚህ መቀየር ትችላለህ
        df = load_data()
        if not df.empty:
            st.metric(label="ጠቅላላ የተመዘገቡ ሰራተኞች", value=len(df))
            # ለአስተዳዳሪው ስልክ ቁጥር ያለበትን ሙሉ ሰንጠረዥ ማሳየት
            st.dataframe(df[["id", "name", "phone", "job_type", "experience"]], use_container_width=True)
        else:
            st.info("እስካሁን ምንም ሰራተኛ አልተመዘገበም።")
    elif password != "":
        st.error("የገቡት ሚስጥራዊ ቁጥር የተሳሳተ ነው!")
