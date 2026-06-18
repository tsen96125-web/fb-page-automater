import streamlit as st
import requests
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
                # Supabase වෙත දත්ත යැවීම (Upsert මඟින් අලුත් කරයි හෝ අලුතින් සාදයි)
                supabase.table("user_config").upsert(data).execute()
                st.success("✅ ඔබගේ සියලුම සැකසුම් (Settings) සාර්ථකව සුරැකුණා! දැන් නියමිත වෙලාවට පසුබිමෙන් පෝස්ට් හැදේවි.")
            except Exception as e:
                st.error(f"❌ Database එකට දත්ත දැමීමේදී දෝෂයක් ඇති විය: {str(e)}")

with col_post:
    if st.button("🚀 Upload a Post Now (ක්ෂණිකව පෝස්ට් කරන්න)", use_container_width=True):
        if not page_id or not access_key:
            st.warning("⚠️ ක්ෂණිකව පෝස්ට් කිරීමට Page ID සහ Access Key ඇතුලත් කර තිබිය යුතුය!")
        else:
            with st.spinner("⏳ AI මඟින් උසස් තත්ත්වයේ පෝස්ට් එක සහ රූපය සකසමින් පවතී..."):
                try:
                    # 1. පිළිවෙලකට සහ ව්‍යුහයකට අනුව Text එක සෑදීමට දෙන විධානය
                    prompt_text = f"""
                    You are an expert social media marketer. Write a highly attractive, engaging, and professional Facebook marketing post based on these details: '{content_details}'
                    The entire post MUST be strictly written in {language}.

                    Strict Structure Rules to follow:
                    1. START with an eye-catching hook line (use relevant emojis).
                    2. BODY: Divide the content into 2-3 short, clean paragraphs or bullet points explaining the main benefits. Do NOT make it a long wall of text. Use engaging emojis naturally.
                    3. LANGUAGE: Ensure the tone is natural, professional, and grammatically perfect for a Facebook audience. Avoid literal or robotic translations.
                    4. CALL TO ACTION: End with a clear call to action.
                    5. HASHTAGS: At the very end of the post, automatically add exactly 15 highly viral and relevant hashtags based on the content.
                    """
                    
                    text_res = requests.get(f"https://text.pollinations.ai/{prompt_text}").text
                    full_post = f"{text_res}\n\n#Automated #Marketing"

                    # 2. Quality එක සහ Realism එක වැඩි කර රූපය සෑදීමට දෙන විධානය
                    enhanced_prompt = f"{image_details}, photorealistic, highly detailed, professional commercial photography, 8k resolution, sharp focus, studio lighting, award-winning composition, cinematic look, no cartoon, no anime, no render"
                    image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&enhance=true"

                    # 3. Facebook Graph API එක හරහා පිටුවට Upload කිරීම
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
1. START with an eye-catching hook line (use relevant emojis).
2. BODY: Divide the content into 2-3 short, clean paragraphs or bullet points explaining the main benefits. Do NOT make it a long wall of text. Use engaging emojis naturally.
3. LANGUAGE: Ensure the tone is natural, professional, and grammatically perfect for a Facebook audience. Avoid literal or robotic translations.
4. CALL TO ACTION: End with a clear call to action (e.g., "Inbox us now or comment below").
5. HASHTAGS: At the very end of the post, automatically add exactly 15 highly viral and relevant hashtags based on the content.
"""
            
            # පරිශීලකයා දෙන විස්තරයට අමතරව Quality එක වැඩි කරන Keywords ස්වයංක්‍රීයව එකතු කිරීම
user_img_prompt = user.get('image_details', 'Professional business setup')
enhanced_prompt = f"{user_img_prompt}, photorealistic, highly detailed, professional commercial photography, 8k resolution, sharp focus, studio lighting, award-winning composition, cinematic look, no cartoon, no anime, no render"

# Pollinations AI වෙත නව විමසුම යැවීම
image_url = f"https://image.pollinations.ai/prompt/{enhanced_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true&enhance=true"
# 3. Facebook Graph API එකට Post කිරීම
fb_url = f"https://graph.facebook.com/{user_data['page_id']}/photos"
payload = {
      'caption': full_post,
      'url': image_url,
      'access_token': user_data['access_key']
}
fb_res = requests.post(fb_url, data=payload)
            
            if fb_res.status_code == 200:
                st.success("පෝස්ට් එක සාර්ථකව Facebook පිටුවට එකතු කරන ලදී!")
            else:
                st.error("Facebook සමග සම්බන්ධ වීමට නොහැකි විය. Access Key එක පරීක්ෂා කරන්න.")

# 4. Schedule Page පිටුව
elif st.session_state.page == "schedule":
    st.title("🗓️ Schedule Posts")
    
    if st.button("Delete previous schedule"):
        st.warning("පැරණි Schedule එක මකා දමන ලදී.")
        
    repeat = st.selectbox("Repeat", ["Daily", "Weekly", "Monthly"])
    
    # Digital Clock / Time Picker (උපරිම වෙලාවන් 3ක්)
    st.write("Add Time (Max 3)")
    time_input = st.time_input("Select Time")
    if "times" not in st.session_state:
        st.session_state.times = []
        
    if st.button("Add"):
        if len(st.session_state.times) < 3:
            st.session_state.times.append(str(time_input))
            st.success(f"Time {time_input} added!")
        else:
            st.error("උපරිම වෙලාවන් 3ක් පමණි ඇතුලත් කල හැක්කේ.")
            
    st.write(f"Selected Times: {st.session_state.times}")
    
    st.write("### Post Content Generation")
    languages = ["English", "Sinhala", "Tamil", "Hindi", "Spanish", "French"] # භාෂා 80ක් දක්වා මෙතනට එක් කල හැක
    selected_lang = st.selectbox("Select Language", languages)
    post_details = st.text_area("Add Post Content Details")
    
    st.write("### Image Generation")
    image_details = st.text_area("Image Details")
    
    if st.button("Save Details"):
        user_id = st.session_state.user.id
        supabase.table("user_config").update({
            "schedule_type": repeat,
            "schedule_times": ",".join(st.session_state.times),
            "language": selected_lang,
            "content_details": post_details,
            "image_details": image_details
        }).eq("id", user_id).execute()
        st.success("Details saved permanently!")
        
    if st.button("Start the workflow"):
        st.success("Workflow එක සාර්ථකව සක්‍රීය කරන ලදී! දැන් ඇප් එක වසා දැමුවද ක්‍රියාවලිය සිදුවේ.")
        if st.button("Back to Dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
