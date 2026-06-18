import os
import requests
from datetime import datetime, timedelta, timezone
from supabase import create_client, Client

# GitHub Secrets වලින් දත්ත ලබා ගැනීම
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase විස්තර අඩුයි!")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. ලංකාවේ වත්මන් වෙලාව සහ දිනය නිවැරදිව ගණනය කිරීම (UTC + 5:30)
sl_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
current_time_str = sl_time.strftime("%H:%M")   # උදාහරණ: "08:00" හෝ "14:30"
current_day = sl_time.strftime("%A")           # සතියේ දිනය (Monday, Tuesday...)
current_date_num = sl_time.day                 # මාසයේ දිනය (1, 2, 3...)

print(f"⏰ ලංකාවේ වත්මන් වෙලාව: {current_time_str} | දිනය: {current_day}")

try:
    # Supabase තුල ඇති පරිශීලක දත්ත ලබා ගැනීම
    response = supabase.table("user_config").select("*").execute()
    users = response.data
except Exception as e:
    print(f"Database කියවීමේ දෝෂයක්: {e}")
    exit(1)

for user in users:
    if not user.get("page_id") or not user.get("access_key"):
        continue
        
    # Schedule දත්ත නොමැති නම් මඟ හැරීම
    if not user.get("schedule_times") or not user.get("schedule_type"):
        continue
        
    # App එකෙන් පරිශීලකයා තේරූ වෙලාවන් පරීක්ෂා කිරීම (උදා: "08:00:00,14:00:00")
    user_times = user["schedule_times"].split(",")
    user_times_formatted = [t[:5] for t in user_times] # තත්පර කොටස අයින් කර "08:00" බවට පත් කිරීම
    
    # වෙලාව ගැලපේදැයි බැලීම
    time_matched = current_time_str in user_times_formatted
    
    # දිනය ගැලපේදැයි බැලීම
    type_matched = False
    sched_type = user["schedule_type"].lower()
    
    if sched_type == "daily":
        type_matched = True
    elif sched_type == "weekly" and current_day == "Monday": # සතියේ සැම සඳුදා දිනකම
        type_matched = True
    elif sched_type == "monthly" and current_date_num == 1:   # සෑම මසකම 1 වෙනිදා
        type_matched = True

    # වෙලාව සහ දිනය දෙකම හරියටම ගැලපේ නම් පමණක් පෝස්ට් එක සිදුවේ
    if time_matched and type_matched:
        print(f"🎯 Schedule එක ගැලපේ! පෝස්ට් එක සකසමින් පවතී... Page: {user['page_id']}")
        try:
            # AI Text Generation
            prompt_text = f"Create a professional, unique marketing post about: {user.get('content_details', 'Business')}. Language: {user.get('language', 'English')}"
            text_response = requests.get(f"https://text.pollinations.ai/{prompt_text}").text
            full_post = f"{text_response}\n\n#Marketing #Automated"
            
            # AI Image Generation
            img_prompt = user.get('image_details', 'Professional business setup')
            image_url = f"https://image.pollinations.ai/prompt/{img_prompt.replace(' ', '%20')}?width=1080&height=1080&nologo=true"
            
            # Facebook Graph API Upload
            fb_url = f"https://graph.facebook.com/{user['page_id']}/photos"
            payload = {
                'caption': full_post,
                'url': image_url,
                'access_token': user['access_key']
            }
            fb_res = requests.post(fb_url, data=payload)
            
            if fb_res.status_code == 200:
                print(f"✅ සාර්ථකව Facebook පිටුවට Upload විය!")
            else:
                print(f"❌ Facebook දෝෂයකි: {fb_res.text}")
        except Exception as e:
            print(f"❌ දෝෂයකි: {str(e)}")
    else:
        print(f"😴 Page: {user['page_id']} සඳහා වෙලාව තවම පැමිණ නැත.")
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
