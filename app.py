import streamlit as st
import requests
import urllib.parse
from supabase import create_client, Client

# Page Configuration (ඇප් එකේ මූලික සැකසුම්)
st.set_page_config(page_title="Facebook Page Automator", page_icon="🚀", layout="centered")

st.title("📱 Facebook Page Automation Panel")
st.write("ඔබගේ Facebook පිටුව ස්වයංක්‍රීයව පවත්වාගෙන යන පද්ධතිය මෙතැනින් පාලනය කරන්න.")

# Supabase සම්බන්ධතාවය පරීක්ෂා කිරීම
try:
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
    st.error("⚠️ Streamlit Secrets වල Supabase විස්තර ඇතුලත් කර නැත! කරුණාකර Settings පරීක්ෂා කරන්න.")
    st.stop()

st.markdown("---")
st.subheader("⚙️ Configuration Settings (සැකසුම්)")

# පරිශීලකයාගෙන් දත්ත ලබාගන්නා කොටස් (Form Inputs)
user_id = st.text_input("User ID (ඔබව හඳුනාගැනීමට කැමති කෙටි නමක් ලබාදෙන්න)", placeholder="Ex: thivanka_01")
page_id = st.text_input("Facebook Page ID", placeholder="Ex: 102938475654321")
access_key = st.text_input("Facebook Page Access Token / Key", type="password", placeholder="EAAZ...")

col1, col2 = st.columns(2)
with col1:
    schedule_type = st.selectbox("Schedule Type (ක්‍රියාත්මක වන වටය)", ["Daily", "Weekly", "Monthly"])
with col2:
    language = st.selectbox("Language (භාෂාව)", ["Sinhala", "English"])

schedule_times = st.text_input("Schedule Times (පෝස්ට් විය යුතු වෙලාවන් - කොමා වලින් වෙන් කරන්න)", value="08:00,14:00,20:00", help="පැය 24 ක්‍රමයට ලියන්න. උදා: 08:00,14:30")

content_details = st.text_area("Post Content Details (AI එකෙන් ලියන්න ඕනේ දේ ගැන විස්තරයක්)", placeholder="Ex: Suwastha Mobile Spa service offering relaxing full body massage therapies in Kegalle area by professional male therapist.")
image_details = st.text_area("Image Details / Prompt (AI එකෙන් හැදෙන්න ඕනේ රූපය ගැන විස්තරයක්)", placeholder="Ex: High quality realistic photo of a luxury spa room with candles, massage table, warm lighting, peaceful environment")

st.markdown("---")

# බොත්තම් ක්‍රියාත්මක වන කොටස (Action Buttons)
col_save, col_post = st.columns(2)

with col_save:
    if st.button("💾 Save Settings to Database", use_container_width=True):
        if not user_id or not page_id or not access_key:
            st.warning("⚠️ කරුණාකර User ID, Page ID සහ Access Key අනිවාර්යයෙන්ම පුරවන්න!")
        else:
            data = {
                "id": user_id,
                "page_id": page_id,
                "access_key": access_key,
                "schedule_type": schedule_type,
                "schedule_times": schedule_times,
                "language": language,
                "content_details": content_details,
                "image_details": image_details
            }
            try:
                supabase.table("user_config").upsert(data).execute()
                st.success("✅ ඔබගේ සියලුම සැකසුම් (Settings) සාර්ථකව සුරැකුණා!")
            except Exception as e:
                st.error(f"❌ Database එකට දත්ත දැමීමේදී දෝෂයක් ඇති විය: {str(e)}")

with col_post:
    if st.button("🚀 Upload a Post Now (ක්ෂණිකව පෝස්ට් කරන්න)", use_container_width=True):
        if not page_id or not access_key:
            st.warning("⚠️ ක්ෂණිකව පෝස්ට් කිරීමට Page ID සහ Access Key ඇතුලත් කර තිබිය යුතුය!")
        else:
            with st.spinner("⏳ AI මඟින් උසස් තත්ත්වයේ පෝස්ට් එක සහ රූපය සකසමින් පවතී..."):
                try:
                    # ආරක්ෂිතව තනි පේළියට Prompt එක සකස් කිරීම
                    raw_prompt = f"Act as an expert social media marketer. Write an attractive, highly engaging and professional Facebook marketing post about: '{content_details}'. The entire post MUST be strictly written in perfect {language}. Structure: 1) Start with an eye-catching hook line using relevant emojis. 2) Body: 2-3 short, clean paragraphs or bullet points explaining main benefits, no long wall of text, use emojis naturally. 3) Tone: natural, perfect grammar for Facebook. 4) Clear call to action at the end. 5) Finish by adding exactly 15 highly viral and relevant hashtags based on the content."
                    
                    # URL එකක් තුලට දැමීමට හැකි වන පරිදි අකුරු හැඩගැස්වීම (URL Encoding)
                    encoded_text_prompt = urllib.parse.quote(raw_prompt)
                    text_res = requests.get(f"https://text.pollinations.ai/{encoded_text_prompt}").text
                    full_post = f"{text_res}\n\n#Automated #Marketing"

                    # Quality එක සහ Realism එක වැඩි කර රූපය සෑදීම
                    enhanced_image_prompt = f"{image_details}, photorealistic, highly detailed, professional commercial photography, 8k resolution, sharp focus, studio lighting, award-winning composition, cinematic look, no cartoon, no anime, no render"
                    encoded_image_prompt = urllib.parse.quote(enhanced_image_prompt)
                    image_url = f"https://image.pollinations.ai/prompt/{encoded_image_prompt}?width=1080&height=1080&nologo=true&enhance=true"

                    # Facebook Graph API එක හරහා පිටුවට Upload කිරීම
                    fb_url = f"https://graph.facebook.com/{page_id}/photos"
                    payload = {
                        'caption': full_post,
                        'url': image_url,
                        'access_token': access_key
                    }
                    fb_res = requests.post(fb_url, data=payload)

                    if fb_res.status_code == 200:
                        st.success("🎉 සාර්ථකයි! පෝස්ට් එක ඔබගේ Facebook පිටුවට ක්ෂණිකව Upload විය.")
                        st.image(image_url, caption="Generated AI Image (High Quality)", use_column_width=True)
                        st.info(f"**Generated Text:**\n\n{full_post}")
                    else:
                        st.error(f"❌ Facebook දෝෂයකි: {fb_res.text}")

                except Exception as e:
                    st.error(f"❌ ක්‍රියාවලිය අතරතුර බලාපොරොත්තු නොවූ දෝෂයක් ඇති විය: {str(e)}")
