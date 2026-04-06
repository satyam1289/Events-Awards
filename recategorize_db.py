import sqlite3

def recategorize_existing_events():
    conn = sqlite3.connect('data/events.db')
    cursor = conn.cursor()
    
    # Update Awards/Honours
    cursor.execute("""
        UPDATE events 
        SET event_type = 'Awards' 
        WHERE event_type IN ('Awards', 'Summit', 'Expo', 'Conclave', 'Forum') 
        AND (event_name LIKE '%award%' OR event_name LIKE '%honour%' OR event_name LIKE '%prize%' OR event_name LIKE '%recognition%')
    """)
    
    # Everyone else is an 'Event'
    cursor.execute("""
        UPDATE events 
        SET event_type = 'Event' 
        WHERE event_type != 'Awards'
    """)
    
    conn.commit()
    conn.close()
    print("Recategorization complete.")

if __name__ == "__main__":
    recategorize_existing_events()
