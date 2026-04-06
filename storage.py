"""
Data Storage - Robust SQLite persistence for scraped events
"""

import sqlite3
import json
import os
import logging
import threading
import datetime
from typing import List, Dict, Optional
import config

# Set up logging
log_level = getattr(logging, str(config.LOG_LEVEL), logging.INFO)
logger = logging.getLogger(__name__)

# Global lock for database access
_db_lock = threading.Lock()

class EventStorage:
    """Handles storage and retrieval of scraped events using SQLite + JSON backup"""
    
    def __init__(self, db_path: str = None, json_path: str = None):
        self.db_path = db_path or os.path.join(config.DATA_DIR, 'events.db')
        self.json_path = json_path or config.EVENTS_FILE
        self._ensure_db()
        self.run_migration()
        self.archive_stale_events()
        self._migrate_from_json()
    
    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _ensure_db(self):
        """Ensure the database and tables exist"""
        with _db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_name TEXT NOT NULL,
                    event_type TEXT,
                    sector TEXT,
                    date TEXT,
                    location TEXT,
                    source_url TEXT,
                    source_title TEXT,
                    confidence INTEGER,
                    scraped_at TEXT,
                    event_key TEXT UNIQUE
                )
            ''')
            conn.commit()
            conn.close()
            logger.info("SQLite database initialized at %s", self.db_path)

    def run_migration(self):
        """Add new columns if they don't exist."""
        NEW_COLUMNS = [
            ("nomination_deadline", "TEXT DEFAULT ''"),
            ("venue", "TEXT DEFAULT ''"),
            ("organizer", "TEXT DEFAULT ''"),
            ("registration_link", "TEXT DEFAULT ''"),
            ("date_start", "TEXT DEFAULT ''"),
            ("date_end", "TEXT DEFAULT ''"),
            ("status", "TEXT DEFAULT 'UPCOMING'"),
            ("last_verified", "TEXT DEFAULT ''"),
            ("days_until_event", "INTEGER DEFAULT -1"),
            ("source_type", "TEXT DEFAULT 'serper'"),
        ]
        
        with _db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Get existing columns
            cursor.execute("PRAGMA table_info(events)")
            existing_columns = [row[1] for row in cursor.fetchall()]
            
            for col_name, col_def in NEW_COLUMNS:
                if col_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE events ADD COLUMN {col_name} {col_def}")
                        logger.info(f"Added column {col_name} to events table.")
                    except Exception as e:
                        logger.error(f"Failed to add column {col_name}: {e}")
            
            conn.commit()
            conn.close()

    def enrich_before_save(self, event: dict) -> dict:
        """Add computed fields before storing."""
        # Compute days until event
        date_str = event.get("date_start") or event.get("date")
        if date_str:
            try:
                import dateparser
                parsed = dateparser.parse(date_str)
                if parsed:
                    delta = (parsed - datetime.datetime.now()).days
                    event["days_until_event"] = delta
                    if delta < 0:
                        event["status"] = config.STATUS_CONCLUDED
                    elif event.get("nomination_deadline"):
                        event["status"] = config.STATUS_NOMINATIONS_OPEN
                    else:
                        event["status"] = config.STATUS_UPCOMING
            except:
                pass
        
        # Auto-detect organizer from source URL
        ORGANIZER_DOMAIN_MAP = {
            "economictimes": "Economic Times",
            "nasscom": "NASSCOM",
            "ficci": "FICCI",
            "cii.in": "CII",
            "yourstory": "YourStory",
            "inc42": "Inc42",
            "businessworld": "Business World",
            "peoplematters": "People Matters",
        }
        url = event.get("source_url", "").lower()
        for domain, org_name in ORGANIZER_DOMAIN_MAP.items():
            if domain in url:
                if not event.get("organizer"):
                    event["organizer"] = org_name
                break
        
        return event

    def _migrate_from_json(self):
        """Migrate legacy JSON data into SQLite. Uses INSERT OR IGNORE to avoid duplicates."""
        if not os.path.exists(self.json_path):
            return
            
        with _db_lock:
            try:
                with open(self.json_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return
                    events = json.loads(content)
                
                if isinstance(events, list):
                    conn = self._get_connection()
                    cursor = conn.cursor()
                    migrated = 0
                    for event in events:
                        event = self.enrich_before_save(event)
                        key = self._create_event_key(event)
                        e_type = event.get('type') or event.get('event_type') or 'Event'
                        
                        cols = [
                            'event_name', 'event_type', 'sector', 'date', 'location', 
                            'source_url', 'source_title', 'confidence', 'scraped_at', 'event_key',
                            'nomination_deadline', 'venue', 'organizer', 'registration_link',
                            'date_start', 'date_end', 'status', 'last_verified', 'days_until_event', 'source_type'
                        ]
                        placeholders = ', '.join(['?' for _ in cols])
                        
                        vals = (
                            event.get('event_name'), e_type, event.get('sector'), event.get('date'), event.get('location'),
                            event.get('source_url'), event.get('source_title'), event.get('confidence', 0),
                            event.get('scraped_at') or datetime.datetime.now().isoformat(), key,
                            event.get('nomination_deadline', ''), event.get('venue', ''), event.get('organizer', ''),
                            event.get('registration_link', ''), event.get('date_start', ''), event.get('date_end', ''),
                            event.get('status', 'UPCOMING'), event.get('last_verified', ''), 
                            event.get('days_until_event', -1), event.get('source_type', 'serper')
                        )
                        
                        cursor.execute(f'INSERT OR IGNORE INTO events ({", ".join(cols)}) VALUES ({placeholders})', vals)
                        if cursor.rowcount > 0:
                            migrated += 1
                    
                    conn.commit()
                    conn.close()
                    if migrated > 0:
                        logger.info("Migration: %d new events imported to SQLite.", migrated)
                
                self.export_to_csv()
                
            except Exception as e:
                logger.error("Global migration failure: %s", e)

    def export_to_csv(self):
        """Export database to CSV for external project usage"""
        import csv
        events = self.get_all_events()
        csv_path = os.path.join(config.DATA_DIR, 'events_export.csv')
        
        # Specific column order for requirements
        fieldnames = [
            'event_name', 'event_type', 'sector', 'date_start', 'date_end', 
            'nomination_deadline', 'days_until_event', 'location', 'venue', 
            'organizer', 'status', 'confidence', 'source_url', 'registration_link', 'scraped_at'
        ]
        
        try:
            if not events:
                return
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                # Freshly compute days_until_event at export time
                for event in events:
                    date_str = event.get("date_start") or event.get("date")
                    if date_str:
                        try:
                            import dateparser
                            parsed = dateparser.parse(date_str)
                            if parsed:
                                event["days_until_event"] = (parsed - datetime.datetime.now()).days
                        except:
                            pass
                
                # Only include requested fields in CSV
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(events)
            logger.info("Exported %d events to CSV: %s", len(events), csv_path)
        except Exception as e:
            logger.error("CSV export failed: %s", e)

    def _create_event_key(self, event: Dict) -> str:
        """Create a unique key to prevent duplicates"""
        name = str(event.get('event_name', '')).lower().replace(' ', '')
        date = str(event.get('date', '')).replace('/', '').replace('-', '').replace(' ', '')
        loc = str(event.get('location', '')).lower().replace(' ', '')
        return f"{name}|{date}|{loc}"

    def add_event(self, event: Dict) -> bool:
        """Add a new event to SQLite and update the JSON backup"""
        event = self.enrich_before_save(event)
        name = event.get('event_name', '')
        if not name or len(name) < 4:
            return False

        key = self._create_event_key(event)
        scraped_at = event.get('scraped_at') or datetime.datetime.now().isoformat()
        
        cols = [
            'event_name', 'event_type', 'sector', 'date', 'location', 
            'source_url', 'source_title', 'confidence', 'scraped_at', 'event_key',
            'nomination_deadline', 'venue', 'organizer', 'registration_link',
            'date_start', 'date_end', 'status', 'last_verified', 'days_until_event', 'source_type'
        ]
        placeholders = ', '.join(['?' for _ in cols])
        
        vals = (
            event.get('event_name'), 
            event.get('type') or event.get('event_type') or 'Event',
            event.get('sector'), event.get('date'), event.get('location'),
            event.get('source_url'), event.get('source_title'), event.get('confidence', 0),
            scraped_at, key,
            event.get('nomination_deadline', ''), event.get('venue', ''), event.get('organizer', ''),
            event.get('registration_link', ''), event.get('date_start', ''), event.get('date_end', ''),
            event.get('status', 'UPCOMING'), event.get('last_verified', ''), 
            event.get('days_until_event', -1), event.get('source_type', 'serper')
        )
        
        with _db_lock:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()
                cursor.execute(f'INSERT INTO events ({", ".join(cols)}) VALUES ({placeholders})', vals)
                conn.commit()
                conn.close()
                self._sync_json()
                logger.info("Stored new event: %s", name)
                return True
            except sqlite3.IntegrityError:
                return False
            except Exception as e:
                logger.error("Failed to store event: %s", e)
                return False

    def _sync_json(self):
        """Export all database records to JSON file for backup/folder storage"""
        events = self.get_all_events()
        try:
            temp_path = self.json_path + '.tmp'
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(events, f, indent=2)
            if os.path.exists(self.json_path):
                os.remove(self.json_path)
            os.rename(temp_path, self.json_path)
        except Exception as e:
            logger.error("JSON sync failed: %s", e)

    def get_all_events(self) -> List[Dict]:
        """Retrieve all events from database"""
        try:
            conn = self._get_connection()
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM events ORDER BY scraped_at DESC")
            rows = cursor.fetchall()
            conn.close()
            
            events = []
            for row in rows:
                ev = dict(row)
                ev['type'] = ev.get('event_type')
                events.append(ev)
            return events
        except Exception as e:
            logger.error("Error retrieving events: %s", e)
            return []

    def get_event_count(self) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM events")
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def get_sector_counts(self) -> Dict:
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT sector, COUNT(*) FROM events GROUP BY sector")
        results = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return results

    def archive_stale_events(self):
        """Move events with confirmed past dates to an archive table."""
        if not getattr(config, 'AUTO_ARCHIVE_CONCLUDED', False):
            return
            
        with _db_lock:
            try:
                conn = self._get_connection()
                # Create archive table if needed
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS events_archive AS 
                    SELECT * FROM events WHERE 1=0
                """)
                
                # Move concluded events
                conn.execute("""
                    INSERT OR IGNORE INTO events_archive 
                    SELECT * FROM events WHERE status = 'CONCLUDED'
                """)
                conn.execute("DELETE FROM events WHERE status = 'CONCLUDED'")
                conn.commit()
                conn.close()
                logger.info("Archived stale (CONCLUDED) events.")
            except Exception as e:
                logger.error(f"Archive failed: {e}")

    def clear_all(self):
        with _db_lock:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM events")
            conn.commit()
            conn.close()
            self._sync_json()
