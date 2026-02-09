import json
import os
import asyncio
from scraper import get_latest_jobs
from emailer import send_email

# Ensure data directory exists
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
DATA_FILE = os.path.join(DATA_DIR, "known_jobs.json")

def ensure_data_dir():
    """Ensure the data directory exists."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"Created data directory: {DATA_DIR}")

def load_known_jobs():
    """Load previously seen job IDs from the JSON file."""
    ensure_data_dir()
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            try:
                data = json.load(f)
                # Handle both list format and clean up any invalid entries
                if isinstance(data, list):
                    # Filter out any invalid IDs like "unknown_id"
                    valid_ids = [job_id for job_id in data if job_id and job_id != "unknown_id"]
                    return set(valid_ids)
                return set()
            except json.JSONDecodeError:
                print("Warning: Could not parse known_jobs.json, starting fresh")
                return set()
    return set()

def save_known_jobs(known_jobs):
    """Save known job IDs to the JSON file."""
    ensure_data_dir()
    # Sort for consistency and readability
    with open(DATA_FILE, "w") as f:
        json.dump(sorted(list(known_jobs)), f, indent=2)
    print(f"Saved {len(known_jobs)} job IDs to {DATA_FILE}")

async def main():
    print("=" * 50)
    print("Microsoft Job Alert Bot - Starting job check...")
    print("=" * 50)
    
    # 1. Load known jobs
    known_jobs = load_known_jobs()
    print(f"Loaded {len(known_jobs)} previously seen jobs.")

    # 2. Scrape current jobs from Microsoft Careers
    print("\nScraping Microsoft Careers page...")
    current_jobs = await get_latest_jobs()
    
    if not current_jobs:
        print("\n❌ No jobs found or scraping failed.")
        print("This could mean:")
        print("  - The Microsoft Careers site structure changed")
        print("  - Network/timeout issues")
        print("  - The page didn't load properly")
        return

    print(f"\n✓ Found {len(current_jobs)} jobs on the page")
    
    # 3. Find new jobs (not seen before)
    new_jobs = []
    
    for job in current_jobs:
        job_id = job.get("id")
        if job_id and job_id not in known_jobs:
            new_jobs.append(job)
            known_jobs.add(job_id)
            print(f"  NEW: {job.get('title', 'Unknown')[:50]}...")
        else:
            # Always add to known_jobs to keep the set current
            if job_id:
                known_jobs.add(job_id)
    
    # 4. Process results
    if new_jobs:
        print(f"\n🎉 Found {len(new_jobs)} NEW job(s)!")
        
        # List all new jobs
        for i, job in enumerate(new_jobs, 1):
            print(f"  {i}. {job.get('title', 'Unknown Position')}")
            print(f"     Location: {job.get('location', 'N/A')}")
            print(f"     Link: {job.get('link', 'N/A')}")
        
        # 5. Send Email notification
        print("\nSending email notification...")
        email_sent = send_email(new_jobs)
        
        if email_sent:
            print("✓ Email sent successfully!")
        else:
            print("⚠ Email sending failed or skipped (check email configuration)")
        
        # 6. Save updated job IDs
        save_known_jobs(known_jobs)
        print("✓ Updated known jobs database")
        
    else:
        print("\nNo new jobs found since last check.")
        # Still save to update the file with any newly validated IDs
        save_known_jobs(known_jobs)
    
    print("\n" + "=" * 50)
    print("Job check complete!")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
