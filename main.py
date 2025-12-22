import re
from colorama import Fore, Back, Style, init
from curl_cffi import requests as curl_requests
from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem
from datetime import datetime, timezone
from dateutil import parser
import uuid
import time
import base64
import json
import random
from typing import Optional, Dict, List, Tuple
import sys

init(autoreset=True)

class Config:
    GITHUB = "https://github.com/Amir-78"
    VERSION = "1.0.0"
    RATE_LIMIT_DELAY = 2
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    REQUEST_TIMEOUT = 30

class RateLimiter:
    def __init__(self, min_delay: float = 2.0):
        self.min_delay = min_delay
        self.last_request = 0
    
    def wait(self):
        elapsed = time.time() - self.last_request
        if elapsed < self.min_delay:
            wait_time = self.min_delay - elapsed
            time.sleep(wait_time)
        self.last_request = time.time()

rate_limiter = RateLimiter(Config.RATE_LIMIT_DELAY)

def print_banner():
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════════════════════════╗
║     {Fore.WHITE}Discord Quest Automation Tool v{Config.VERSION}{Fore.CYAN}                  ║
║     {Fore.YELLOW}GitHub: {Config.GITHUB}{Fore.CYAN}                    ║
╚═══════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def print_section(title: str):
    print(f"\n{Fore.CYAN}{'═' * 60}")
    print(f"{Fore.WHITE}{title.center(60)}")
    print(f"{Fore.CYAN}{'═' * 60}{Style.RESET_ALL}\n")

def print_success(message: str):
    print(f"{Fore.GREEN}✓ {Fore.WHITE}{message}{Style.RESET_ALL}")

def print_error(message: str):
    print(f"{Fore.RED}✗ {Fore.WHITE}{message}{Style.RESET_ALL}")

def print_info(message: str):
    print(f"{Fore.CYAN}ℹ  {Fore.WHITE}{message}{Style.RESET_ALL}")

def print_warning(message: str):
    print(f"{Fore.YELLOW}⚠  {Fore.WHITE}{message}{Style.RESET_ALL}")

def handle_rate_limit(response) -> bool:

    if response.status_code == 429:
        try:
            rate_limit_data = response.json()
            retry_after = rate_limit_data.get("retry_after", 60)
            
            print_warning(f"Rate limited! Waiting {retry_after:.2f} seconds...")

            if retry_after > 10:
                for remaining in range(int(retry_after), 0, -10):
                    print(f"{Fore.YELLOW}⏳ {remaining} seconds remaining...{Style.RESET_ALL}")
                    time.sleep(10)
                time.sleep(retry_after % 10)
            else:
                time.sleep(retry_after)
            
            print_success("Rate limit wait completed, continuing...")
            return True
        except Exception as e:
            print_error(f"Error parsing rate limit response: {str(e)}")
            print_warning("Waiting 60 seconds as fallback...")
            time.sleep(60)
            return True
    return False

def get_valid_useragent() -> Tuple[str, int]:
    ua_generator = UserAgent(
        software_names=[SoftwareName.CHROME.value],
        operating_systems=[OperatingSystem.WINDOWS.value],
        limit=1000,
    )

    while True:
        ua = ua_generator.get_random_user_agent()
        match = re.search(r"Chrome/(\d+)", ua)
        if match:
            version = int(match.group(1))
            if 100 <= version <= 999:
                return ua, version

def build_sec_ch_ua() -> Tuple[str, str]:
    ua, version = get_valid_useragent()
    sec_ch_ua = (
        f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not_A Brand";v="24"'
    )
    return ua, sec_ch_ua

def generate_x_super_properties(useragent: Tuple[str, int]) -> str:
    if "Firefox" in useragent[0]:
        browser_name = "Firefox"
        browser_version = useragent[0].split("Firefox/")[-1]
    elif "OPR" in useragent[0] or "Opera" in useragent[0]:
        browser_name = "Opera"
        browser_version = useragent[0].split("OPR/")[-1].split(" ")[0]
    else:
        browser_name = "Chrome"
        browser_version = useragent[0].split("Chrome/")[1].split(" ")[0]
    
    super_props = {
        "os": "Windows",
        "browser": browser_name,
        "device": "",
        "system_locale": "en-US",
        "has_client_mods": False,
        "browser_user_agent": useragent[0],
        "browser_version": browser_version,
        "os_version": "10",
        "referrer": "",
        "referring_domain": "",
        "referrer_current": "",
        "referring_domain_current": "",
        "release_channel": "stable",
        "client_build_number": random.randint(400_000, 500_000),
        "client_event_source": None,
        "client_launch_id": str(uuid.uuid4()),
        "launch_signature": str(uuid.uuid4()),
        "client_app_state": "unfocused",
    }

    x_super_properties = base64.b64encode(json.dumps(super_props).encode()).decode()
    return x_super_properties

def get_fingerprint(session, useragent: Tuple[str, int], xsuper_properties: str) -> Optional[str]:
    for attempt in range(Config.MAX_RETRIES):
        try:
            rate_limiter.wait()
            
            headers = {
                "Accept": "*/*",
                "Accept-Encoding": "gzip, deflate, br, zstd",
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Connection": "keep-alive",
                "Host": "discord.com",
                "Referer": "https://discord.com/register",
                "sec-ch-ua": f'"Chromium";v="{useragent[1]}", "Not)A;Brand";v="8"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "Sec-Fetch-Dest": "empty",
                "Sec-Fetch-Mode": "cors",
                "Sec-Fetch-Site": "same-origin",
                "User-Agent": useragent[0],
                "X-Context-Properties": "eyJsb2NhdGlvbiI6IlJlZ2lzdGVyIn0=",
                "X-Debug-Options": "bugReporterEnabled",
                "X-Discord-Locale": "en-US",
                "X-Discord-Timezone": "America/New_York",
                "X-Super-Properties": xsuper_properties,
            }
            
            response = session.get(
                "https://discord.com/api/v9/experiments?with_guild_experiments=true",
                headers=headers,
                timeout=Config.REQUEST_TIMEOUT
            )
            
            if handle_rate_limit(response):
                continue
            
            if response.status_code == 200:
                fingerprint = response.json()["fingerprint"]
                print_success(f"Fingerprint obtained: {Fore.YELLOW}{fingerprint}")
                return fingerprint
            else:
                print_error(f"Failed to get fingerprint - Status: {response.status_code}")
                if attempt < Config.MAX_RETRIES - 1:
                    print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                    time.sleep(Config.RETRY_DELAY)
        except Exception as e:
            print_error(f"Fingerprint error: {str(e)}")
            if attempt < Config.MAX_RETRIES - 1:
                print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                time.sleep(Config.RETRY_DELAY)
    
    return None

def get_quests(token: str, useragent: Tuple[str, int], xsuper_properties: str) -> Optional[List[Dict]]:
    for attempt in range(Config.MAX_RETRIES):
        try:
            rate_limiter.wait()
            
            headers = {
                "authorization": token,
                "referer": "https://discord.com/quest-home",
                "sec-ch-ua": f'"Chromium";v="{useragent[1]}", "Not)A;Brand";v="8"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": useragent[0],
                "x-super-properties": xsuper_properties,
            }
            
            response = curl_requests.get(
                "https://discord.com/api/v9/quests/@me",
                headers=headers,
                timeout=Config.REQUEST_TIMEOUT
            )

            if handle_rate_limit(response):
                continue
            
            if response.status_code == 200:
                return response.json()["quests"]
            else:
                print_error(f"Failed to fetch quests - Status: {response.status_code}")
                if attempt < Config.MAX_RETRIES - 1:
                    print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                    time.sleep(Config.RETRY_DELAY)
        except Exception as e:
            print_error(f"Quest fetch error: {str(e)}")
            if attempt < Config.MAX_RETRIES - 1:
                print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                time.sleep(Config.RETRY_DELAY)
    
    return None

def enroll_quest(token: str, quest_id: str, useragent: Tuple[str, int], xsuper_properties: str) -> Optional[object]:
    for attempt in range(Config.MAX_RETRIES):
        try:
            rate_limiter.wait()
            
            headers = {
                "authorization": token,
                "referer": "https://discord.com/quest-home",
                "sec-ch-ua": f'"Chromium";v="{useragent[1]}", "Not)A;Brand";v="8"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"',
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": useragent[0],
                "x-super-properties": xsuper_properties,
            }
            
            enroll_json = {
                "location": 11,
                "is_targeted": False,
                "metadata_raw": None,
                "metadata_sealed": None,
            }
            
            response = curl_requests.post(
                f"https://discord.com/api/v9/quests/{quest_id}/enroll",
                json=enroll_json,
                headers=headers,
                timeout=Config.REQUEST_TIMEOUT
            )

            if handle_rate_limit(response):
                continue

            return response
            
        except Exception as e:
            print_error(f"Enrollment error: {str(e)}")
            if attempt < Config.MAX_RETRIES - 1:
                print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                time.sleep(Config.RETRY_DELAY)
    
    return None

def solve_quest(token: str, quest_id: str, quest_name: str, video_length: int, useragent: Tuple[str, int], xsuper_properties: str) -> bool:
    try:
        print_info(f"Enrolling in: {Fore.YELLOW}{quest_name}")
        enroll_quest(token, quest_id, useragent, xsuper_properties)
        time.sleep(2)
        
        response = enroll_quest(token, quest_id, useragent, xsuper_properties)
        
        if not response:
            print_error(f"Failed to enroll in {quest_name} - No response")
            return False
            
        if response.status_code != 200:
            print_error(f"Failed to enroll in {quest_name} - Status: {response.status_code}")
            try:
                print_error(f"Response: {response.text}")
            except:
                pass
            return False
        
        print_success(f"Enrolled in: {quest_name}")
        time.sleep(3)

        base_increment = video_length / 8
        
        if base_increment > 8:
            num_updates = int(video_length / 8)
            increment = 8
        else:
            num_updates = 8
            increment = base_increment
        
        progress_points = []
        current_progress = 0
        
        for i in range(num_updates):
            if i == num_updates - 1:
                progress_points.append(video_length)
            else:
                variation = random.uniform(-1, 1)
                current_progress += int(increment + variation)
                current_progress = min(current_progress, video_length - 1)
                progress_points.append(current_progress)
        
        print_info(f"Simulating realistic video progress with {num_updates} updates...")

        for idx, timestamp in enumerate(progress_points, 1):
            for attempt in range(Config.MAX_RETRIES):
                rate_limiter.wait()
                
                headers = {
                    "authorization": token,
                    "referer": "https://discord.com/quest-home",
                    "sec-ch-ua": f'"Chromium";v="{useragent[1]}", "Not)A;Brand";v="8"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-origin",
                    "user-agent": useragent[0],
                    "x-super-properties": xsuper_properties,
                }
                if timestamp > video_length:
                    timestamp = video_length
                solve_data = {"timestamp": timestamp}
                response = curl_requests.post(
                    f"https://discord.com/api/v9/quests/{quest_id}/video-progress",
                    json=solve_data,
                    headers=headers,
                    timeout=Config.REQUEST_TIMEOUT
                )

                if handle_rate_limit(response):
                    continue
                
                if response.status_code == 200:
                    video_progress = response.json().get("progress", {})
                    WATCH_VIDEO = video_progress.get("WATCH_VIDEO", {})
                    WATCH_VIDEO_ON_MOBILE = video_progress.get("WATCH_VIDEO_ON_MOBILE", {})
                    video_value = WATCH_VIDEO.get("value") or WATCH_VIDEO_ON_MOBILE.get("value")
                    
                    print_info(f"Progress update {idx}/{num_updates}: {timestamp}s (Current: {video_value}s)")
                    
                    if video_value == video_length:
                        print_success(f"{quest_name} is ready to claim!")
                        return True
                    
                    if idx < len(progress_points):
                        time.sleep(random.uniform(3.5,7.8))
                    break
                    
                elif response.status_code == 400:
                    print_warning(f"Bad request at {timestamp}s - Quest might be completed or invalid")
                    try:
                        print_warning(f"Response: {response.text}")
                    except:
                        pass
                    if timestamp >= video_length:
                        return True
                    return False
                else:
                    print_error(f"Failed to submit progress - Status: {response.status_code}")
                    try:
                        print_error(f"Response: {response.text}")
                    except:
                        pass
                    
                    if attempt < Config.MAX_RETRIES - 1:
                        print_info(f"Retrying... (Attempt {attempt + 2}/{Config.MAX_RETRIES})")
                        time.sleep(Config.RETRY_DELAY)
                    else:
                        return False
            
    except Exception as e:
        print_error(f"Quest solve error: {str(e)}")
        return False
    
    return False

def filter_video_quests(quests: List[Dict]) -> List[Dict]:
    now = datetime.now(timezone.utc)
    video_quests = []

    for q in quests:
        config = q.get("config", {})
        user_status = q.get("user_status", {})
        task_config = config.get("task_config", {})
        tasks = task_config.get("tasks", {})

        starts_at = config.get("starts_at")
        expires_at = config.get("expires_at")

        if not (starts_at and expires_at):
            continue

        try:
            starts_dt = parser.isoparse(starts_at)
            expires_dt = parser.isoparse(expires_at)

            if (
                starts_dt <= now <= expires_dt
                and (tasks.get("WATCH_VIDEO") or tasks.get("WATCH_VIDEO_ON_MOBILE"))
                and (not user_status or not user_status.get("completed_at"))
            ):
                video_quests.append(q)
        except Exception as e:
            print_warning(f"Error parsing quest dates: {str(e)}")
            continue

    return video_quests

def main():
    print_banner()
    
    TOKEN = input(f"{Fore.CYAN}Enter your Discord account token: {Fore.WHITE}").strip()
    
    if not TOKEN:
        print_error("Token cannot be empty!")
        sys.exit(1)
    
    print_section("Initializing Session")

    useragent = get_valid_useragent()
    xsuper_properties = generate_x_super_properties(useragent)
    
    print_info(f"User-Agent: {Fore.YELLOW}{useragent[0][:60]}...")
    print_info(f"Chrome Version: {Fore.YELLOW}{useragent[1]}")

    session = curl_requests.Session()
    fingerprint = get_fingerprint(session, useragent, xsuper_properties)
    
    if fingerprint:
        print_success("Session initialized successfully")
    else:
        print_warning("Failed to get fingerprint, continuing anyway...")

    print_section("Fetching Quests")
    
    current_quests = get_quests(TOKEN, useragent, xsuper_properties)
    if not current_quests:
        print_error("Failed to fetch quests. Please check your token.")
        sys.exit(1)
    
    print_success(f"Total quests found: {Fore.YELLOW}{len(current_quests)}")

    video_quests = filter_video_quests(current_quests)
    print_success(f"Solvable video quests: {Fore.YELLOW}{len(video_quests)}")
    
    if not video_quests:
        print_info("No video quests available to solve at this time.")
        return

    print_section("Solving Quests")
    
    solved_count = 0
    failed_count = 0
    
    for idx, video_quest in enumerate(video_quests, 1):
        video_config = video_quest.get("config", {})
        quest_name = video_config.get("messages", {}).get("game_title", "Unknown Quest")
        
        print(f"\n{Fore.CYAN}[{idx}/{len(video_quests)}] {Fore.WHITE}Processing: {Fore.YELLOW}{quest_name}")
        
        video_task_config = video_config.get("task_config", {})
        video_tasks = video_task_config.get("tasks", {})
        WATCH_VIDEO = video_tasks.get("WATCH_VIDEO", {})
        WATCH_VIDEO_ON_MOBILE = video_tasks.get("WATCH_VIDEO_ON_MOBILE", {})
        target_length = WATCH_VIDEO.get("target") or WATCH_VIDEO_ON_MOBILE.get("target")
        
        if solve_quest(TOKEN, video_quest["id"], quest_name, target_length, useragent, xsuper_properties):
            solved_count += 1
        else:
            failed_count += 1
        
        if idx < len(video_quests):
            print_info(f"Waiting 30 seconds before next quest...")
            time.sleep(30)

    print_section("Summary")
    print_success(f"Quests solved: {solved_count}")
    if failed_count > 0:
        print_error(f"Quests failed: {failed_count}")
    print_info(f"Total processed: {solved_count + failed_count}")
    print(f"\n{Fore.MAGENTA}Go back to Discord and claim the rewards!\n{Fore.CYAN}Thanks for using Discord Quest Automation!")
    print(f"{Fore.YELLOW}GitHub: {Config.GITHUB}{Style.RESET_ALL}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}Operation cancelled by user.{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        sys.exit(1)