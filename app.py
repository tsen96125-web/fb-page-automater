import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from supabase import create_client, Client

# Supabase සම්බන්ධතාවය (ඔබගේ Keys පසුව ඇතුලත් කරන්න)
SUPABASE_URL = st.secrets["https://otjrumeewtcokfscyvgd.supabase.co"]
SUPABASE_KEY = st.secrets["sb_publishable_5lukLFLWWhA-0fKrqiVpmw_s-LWzj_p"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="FB Page Automater", layout="centered")

# Session State පාලනය
if "user" not in st.session_state:
    st.session_state.user = None
if "page" not in st.session_state:
    st.session_state.page = "login"

# --- පිටු පාලනය (Page Navigation) ---

# 1. Login & Registration පිටුව
if st.session_state.page == "login":
    st.title("🔐 FB Page Automater - Login")
    tab1, tab2 = st.tabs(["Sign In", "Sign Up"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Log In"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                # කලින් දත්ත ඇත්දැයි බැලීම
                config = supabase.table("user_config").select("*").eq("id", res.user.id).execute()
                if config.data:
                    st.session_state.page = "dashboard"
                else:
                    st.session_state.page = "connect_fb"
                st.rerun()
            except Exception as e:
                st.error(f"Login වැරදියි: {str(e)}")
                
    with tab2:
        new_email = st.text_input("New Email", key="reg_email")
        new_password = st.text_input("New Password", type="password", key="reg_pass")
        if st.button("Register & Send Verification"):
            try:
                supabase.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Verification Email එකක් ඔබගේ ලිපිනයට යවන ලදි. කරුණාකර එය Verify කර Log වන්න.")
            except Exception as e:
                st.error(f"ලියාපදිංචිය අසාර්ථකයි: {str(e)}")

# 2. Connect Facebook Page පිටුව
elif st.session_state.page == "connect_fb":
    st.title("🔗 Connect your Facebook Page")
    page_id = st.text_input("Enter your Facebook Page ID")
    access_key = st.text_input("Enter the Page Access Key", type="password")
    
    if st.button("Save Information"):
        if page_id and access_key:
            try:
                supabase.table("user_config").insert({
                    "id": st.session_state.user.id,
                    "page_id": page_id,
                    "access_key": access_key
                }).execute()
                st.success("Information saved successfully!")
                st.session_state.page = "dashboard"
                st.rerun()
            except Exception as e:
                st.error(f"සුරැකීමට නොහැකි විය: {str(e)}")
        else:
            st.warning("කරුණාකර සියලු විස්තර ඇතුලත් කරන්න.")

# 3. Dashboard පිටුව
elif st.session_state.page == "dashboard":
    st.title("📊 FB Page Automater")
    
    # Facebook විස්තර පෙන්වීම (Mocking Data for UI and real connectivity setup)
    user_id = st.session_state.user.id
    user_data = supabase.table("user_config").select("*").eq("id", user_id).execute().data[0]
    
    st.subheader(f"Connected Page ID: {user_data['page_id']}")
    
    # Analytics ප්‍රස්ථාර (Graphs)
    st.write("### Page Performance")
    chart_data = pd.DataFrame({"Days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"], "Followers Growth": [10, 23, 35, 45, 60, 82, 100]})
    st.line_chart(chart_data.set_index("Days"))
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗓️ Schedule Posts", use_container_width=True):
            st.session_state.page = "schedule"
            st.rerun()
    with col2:
        if st.button("🚀 Upload a Post Now", use_container_width=True):
            st.info("AI මගින් Post එක සහ ඡායාරූපය නිපදවමින් පවතී...")
            
            # 1. AI Text Generation (Pollinations AI Free endpoint)
            prompt_text = f"Create a professional, unique marketing post about: {user_data.get('content_details', 'Business')}. Language: {user_data.get('language', 'English')}"
            text_response = requests.get(f"https://text.pollinations.ai/{prompt_text}").text
            full_post = f"{text_response}\n\n#Marketing #Automated"
            
            # 2. AI Image Generation (Pollinations Image endpoint)
            img_prompt = user_data.get('image_details', 'Professional business setup')
            image_url = f"https://image.pollinations.ai/prompt/{img_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true"
            
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
