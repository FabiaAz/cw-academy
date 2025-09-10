# agent-memory/utils/database.py
import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "memory.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT
        )
    """)
    conn.commit()
    conn.close()


def _to_iso(date_str: str):
    if not date_str:
        return None
    formats = ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d")
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date().isoformat()
        except Exception:
            continue
    # try ISO directly
    try:
        return datetime.fromisoformat(date_str).date().isoformat()
    except Exception:
        return None


def save_event(date: str, description: str):
    """Salva um evento convertendo a data para ISO (YYYY-MM-DD)."""
    iso_date = _to_iso(date) or datetime.now().date().isoformat()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (date, description) VALUES (?, ?)", (iso_date, description))
    conn.commit()
    conn.close()


def search_events(query: str):
    """
    Busca por palavra-chave (na descrição) ou por data (aceita dd/mm/YYYY ou yyyy-mm-dd).
    Retorna lista de tuplas (id, date_iso, description).
    """
    iso = _to_iso(query)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if iso:
        cursor.execute("""
            SELECT id, date, description
            FROM events
            WHERE date = ? OR description LIKE ?
            ORDER BY date ASC
        """, (iso, f"%{query}%"))
    else:
        cursor.execute("""
            SELECT id, date, description
            FROM events
            WHERE date LIKE ? OR description LIKE ?
            ORDER BY date ASC
        """, (f"%{query}%", f"%{query}%"))
    results = cursor.fetchall()
    conn.close()
    return results


def search_events_by_date(start_date: str, end_date: str):
    """Busca eventos entre start_date e end_date (aceita dd/mm/YYYY ou yyyy-mm-dd)."""
    iso_start = _to_iso(start_date) or datetime.now().date().isoformat()
    iso_end = _to_iso(end_date) or iso_start
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, date, description 
        FROM events 
        WHERE date BETWEEN ? AND ?
        ORDER BY date ASC
    """, (iso_start, iso_end))
    results = cursor.fetchall()
    conn.close()
    return results
