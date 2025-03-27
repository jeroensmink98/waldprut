import sqlite3
from datetime import datetime
from typing import List
from models import NewsItem, Reaction, NestedReaction, Image

def init_db():
    """Initialize the database with required tables."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    # Create news_items table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS news_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        category TEXT,
        reactions_info TEXT,
        reactions_link TEXT,
        article_link TEXT,
        image_url TEXT,
        image_alt TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create reactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        news_item_id INTEGER,
        user TEXT,
        text TEXT,
        language TEXT,
        likes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (news_item_id) REFERENCES news_items (id)
    )
    ''')
    
    # Create nested_reactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS nested_reactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reaction_id INTEGER,
        text TEXT,
        language TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (reaction_id) REFERENCES reactions (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def store_news_item(news_item: NewsItem) -> int:
    """Store a news item and its reactions in the database."""
    print(f"Attempting to store news item: {news_item.title}")
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    try:
        # Convert URLs to strings
        reactions_link_str = str(news_item.reactions_link) if news_item.reactions_link else None
        article_link_str = str(news_item.article_link) if news_item.article_link else None
        image_url_str = str(news_item.image.url) if news_item.image and news_item.image.url else None
        
        # Insert news item
        print("Inserting news item into database...")
        cursor.execute('''
        INSERT INTO news_items (title, category, reactions_info, reactions_link, 
                              article_link, image_url, image_alt)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            news_item.title,
            news_item.category,
            news_item.reactions_info,
            reactions_link_str,
            article_link_str,
            image_url_str,
            news_item.image.alt if news_item.image else None
        ))
        
        news_item_id = cursor.lastrowid
        print(f"Successfully inserted news item with ID: {news_item_id}")
        
        # Insert reactions
        print(f"Inserting {len(news_item.reactions)} reactions...")
        for reaction in news_item.reactions:
            cursor.execute('''
            INSERT INTO reactions (news_item_id, user, text, language, likes)
            VALUES (?, ?, ?, ?, ?)
            ''', (
                news_item_id,
                reaction.user,
                reaction.text,
                reaction.language,
                reaction.likes
            ))
            
            reaction_id = cursor.lastrowid
            print(f"Inserted reaction with ID: {reaction_id}")
            
            # Insert nested reactions
            print(f"Inserting {len(reaction.nested_reactions)} nested reactions...")
            for nested in reaction.nested_reactions:
                cursor.execute('''
                INSERT INTO nested_reactions (reaction_id, text, language)
                VALUES (?, ?, ?)
                ''', (
                    reaction_id,
                    nested.text,
                    nested.language
                ))
        
        conn.commit()
        print("Successfully committed all changes to database")
        return news_item_id
        
    except Exception as e:
        print(f"Error storing news item: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_latest_news_items(limit: int = 10) -> List[NewsItem]:
    """Retrieve the latest news items from the database."""
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
        SELECT id, title, category, reactions_info, reactions_link, 
               article_link, image_url, image_alt
        FROM news_items
        ORDER BY created_at DESC
        LIMIT ?
        ''', (limit,))
        
        news_items = []
        for row in cursor.fetchall():
            news_item = NewsItem(
                title=row[1],
                category=row[2],
                reactions_info=row[3],
                reactions_link=row[4],
                article_link=row[5],
                image=Image(url=row[6], alt=row[7]) if row[6] else None,
                reactions=[]  # We'll fetch reactions separately
            )
            
            # Fetch reactions for this news item
            cursor.execute('''
            SELECT id, user, text, language, likes
            FROM reactions
            WHERE news_item_id = ?
            ''', (row[0],))
            
            for react_row in cursor.fetchall():
                # Fetch nested reactions
                cursor.execute('''
                SELECT text, language
                FROM nested_reactions
                WHERE reaction_id = ?
                ''', (react_row[0],))
                
                nested_reactions = [
                    NestedReaction(text=nr[0], language=nr[1])
                    for nr in cursor.fetchall()
                ]
                
                reaction = Reaction(
                    user=react_row[1],
                    text=react_row[2],
                    language=react_row[3],
                    likes=react_row[4],
                    nested_reactions=nested_reactions
                )
                news_item.reactions.append(reaction)
            
            news_items.append(news_item)
        
        return news_items
        
    finally:
        conn.close() 