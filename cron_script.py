import os
import requests
from datetime import datetime
from supabase import create_client, Client

# GitHub Secrets වලින් දත්ත ලබා ගැනීම
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase විස්තර අඩුයි!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    # සියලුම පරිශීලකයන්ගේ දත්ත පරීක්ෂා කිරීම
    response = supabase.table("user_config").select("*").execute()
    users = response.data
except Exception as e:
    print(f"Database කියවීමේ දෝෂයක්: {e}")
    exit(1)

for user in users:
    # Facebook දත්ත නොමැති නම් මඟ හැරීම
    if not user.get("page_id") or not user.get("access_key"):
        continue
        
    print(f"Processing Page: {user['page_id']}")
    
    try:
        # 1. AI Text Generation (Pollinations AI)
        prompt_text = f"Create a professional, unique marketing post about: {user.get('content_details', 'Business')}. Language: {user.get('language', 'English')}"
        text_response = requests.get(f"https://text.pollinations.ai/{prompt_text}").text
        full_post = f"{text_response}\n\n#Marketing #Automated"
        
        # 2. AI Image Generation
        img_prompt = user.get('image_details', 'Professional business setup')
        image_url = f"https://image.pollinations.ai/prompt/{img_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true"
        
        # 3. Facebook Graph API එකට Upload කිරීම
        fb_url = f"https://graph.facebook.com/{user['page_id']}/photos"
        payload = {
            'caption': full_post,
            'url': image_url,
            'access_token': user['access_key']
        }
        fb_res = requests.post(fb_url, data=payload)
        
        if fb_res.status_code == 200:
            print(f"සාර්ථකව Page එකට පෝස්ට් විය: {user['page_id']}")
        else:
            print(f"Facebook දෝෂයකි: {fb_res.text}")
            
    except Exception as e:
        print(f"ක්‍රියාවලියේ දෝෂයකි: {str(e)}")
