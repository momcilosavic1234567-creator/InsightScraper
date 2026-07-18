import os
import sqlite3
import pandas as pd
from datetime import datetime

VALID_STATUSES = {"New", "Favorite", "Applied", "Rejected"}

DEFAULT_DB_PATH = os.path.join("data", "jobs.db")

def init_db(db_path=DEFAULT_DB_PATH):
    """Initializes the SQLite database and creates the jobs table if it doesn't exist."""
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            link TEXT UNIQUE NOT NULL,
            date_posted TEXT,
            source TEXT NOT NULL,
            scraped_at TEXT NOT NULL,
            status TEXT DEFAULT 'New',
            notes TEXT DEFAULT ''
        )
        """
    )

    cursor.execute("PRAGMA table_info(jobs)")
    columns = {row[1] for row in cursor.fetchall()}
    if "status" not in columns:
        cursor.execute("ALTER TABLE jobs ADD COLUMN status TEXT DEFAULT 'New'")
    if "notes" not in columns:
        cursor.execute("ALTER TABLE jobs ADD COLUMN notes TEXT DEFAULT ''")

    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link)")
    conn.commit()
    conn.close()

def save_jobs(jobs, db_path=DEFAULT_DB_PATH):
    """
    Saves a list of job dicts to the database.
    Prevents duplicates based on the unique 'link' constraint.
    Returns the list of newly inserted job objects.
    """
    if not jobs:
        return []

    init_db(db_path)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    new_jobs = []
    scraped_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    for job in jobs:
        link = (job.get("link") or "").strip()
        if not link:
            continue

        try:
            cursor.execute(
                """
                INSERT INTO jobs (title, company, location, link, date_posted, source, scraped_at, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'New', '')
                """,
                (
                    (job.get("title") or "N/A").strip() or "N/A",
                    (job.get("company") or "N/A").strip() or "N/A",
                    (job.get("location") or "N/A").strip() or "N/A",
                    link,
                    (job.get("date_posted") or "N/A").strip() or "N/A",
                    (job.get("source") or "Unknown").strip() or "Unknown",
                    scraped_at
                )
            )
            # preserve the inserted job shape with new metadata for notification and reporting
            inserted_job = {
                **job,
                "status": "New",
                "scraped_at": scraped_at
            }
            new_jobs.append(inserted_job)
        except sqlite3.IntegrityError:
            # Duplicate URL/link, skip
            pass
            
    conn.commit()
    conn.close()
    return new_jobs

def get_all_jobs(db_path=DEFAULT_DB_PATH):
    """Retrieves all jobs from the database and returns them as a pandas DataFrame."""
    init_db(db_path)
    conn = sqlite3.connect(db_path)
    try:
        df = pd.read_sql_query("SELECT * FROM jobs ORDER BY scraped_at DESC, id DESC", conn)
        return df
    finally:
        conn.close()

def update_job_status(job_id, status, db_path=DEFAULT_DB_PATH):
    """Updates the status of a job (e.g. 'New', 'Favorite', 'Applied', 'Rejected')."""
    normalized_status = status.strip() if isinstance(status, str) else "New"
    if normalized_status not in VALID_STATUSES:
        normalized_status = "New"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jobs SET status = ? WHERE id = ?",
        (normalized_status, job_id)
    )
    conn.commit()
    conn.close()

def update_job_notes(job_id, notes, db_path=DEFAULT_DB_PATH):
    """Updates the notes field for a specific job."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE jobs SET notes = ? WHERE id = ?",
        (notes, job_id)
    )
    conn.commit()
    conn.close()
