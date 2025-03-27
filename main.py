import requests
from bs4 import BeautifulSoup
import time
from langdetect import detect
from models import NewsItem, Reaction, NestedReaction, Image
from typing import List

NEWS_PAGE = "https://www.waldnet.nl/nieuws.php"

# Define headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

def detect_language(text: str) -> str:
    """Detect if text is Dutch (NL) or Frisian (FR)."""
    try:
        lang = detect(text)
        return 'NL' if lang == 'nl' else 'FR'
    except:
        return 'FR'  # Default to FR if detection fails

def get_reactions(reactions_url: str) -> List[Reaction]:
    """Fetch and parse reactions from a reactions page."""
    try:
        response = requests.get(reactions_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        reactions = []
        # Find all reaction divs
        for reactie_div in soup.find_all('div', class_='reactie'):
            # Get user info
            user = "Unknown"
            user_nickname = reactie_div.find('div', class_='usernickname')
            if user_nickname and user_nickname.find('span'):
                user = user_nickname.find('span').text.strip()
            
            # Get reaction text and language
            text = ""
            language = "Unknown"
            text_p = reactie_div.find('p')
            if text_p:
                text = text_p.text.strip()
                language = detect_language(text)
            
            # Get likes
            likes = "0"
            date_div = reactie_div.find_next('div', class_='reaksje_datum')
            if date_div and date_div.find('span', class_='like-count'):
                likes = date_div.find('span', class_='like-count').text.strip()
            
            # Get nested reactions
            nested_reactions = []
            nested_div = reactie_div.find_next('div', class_='geneste-reacties')
            if nested_div:
                for nested_reactie in nested_div.find_all('div', class_='reactie'):
                    nested_text = ""
                    nested_language = "Unknown"
                    nested_text_p = nested_reactie.find('p')
                    if nested_text_p:
                        nested_text = nested_text_p.text.strip()
                        nested_language = detect_language(nested_text)
                    
                    nested_reactions.append(NestedReaction(
                        text=nested_text,
                        language=nested_language
                    ))
            
            # Create Reaction object
            reaction = Reaction(
                user=user,
                text=text,
                language=language,
                likes=likes,
                nested_reactions=nested_reactions
            )
            reactions.append(reaction)
        
        return reactions
    except Exception as e:
        print(f"Error fetching reactions: {e}")
        return []

def print_news_item(news_item: NewsItem) -> None:
    """Print a news item in a formatted way."""
    print(f"\nTitle: {news_item.title}")
    print(f"Category: {news_item.category}")
    print(f"Reactions info: {news_item.reactions_info}")
    if news_item.reactions_link:
        print(f"Reactions link: {news_item.reactions_link}")
    
    if news_item.reactions:
        print("\nReactions:")
        for i, reaction in enumerate(news_item.reactions, 1):
            print(f"\nReaction {i}:")
            print(f"User: {reaction.user}")
            print(f"Text: {reaction.text}")
            print(f"Language: {reaction.language}")
            print(f"Likes: {reaction.likes}")
            
            if reaction.nested_reactions:
                print("\nNested reactions:")
                for j, nested in enumerate(reaction.nested_reactions, 1):
                    print(f"  {j}. {nested.text} [{nested.language}]")
    
    print(f"Article link: {news_item.article_link}")
    if news_item.image:
        print(f"Image: {news_item.image.url}")
        print(f"Image alt: {news_item.image.alt}")
    print("-" * 50)

try:
    # Fetch the page content with headers
    print("Fetching news page...")
    response = requests.get(NEWS_PAGE, headers=headers)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items_html = soup.find_all('div', class_='nieuws-item')
        
        for news_item_html in news_items_html[:10]:
            # Get the title
            title = ""
            title_elem = news_item_html.find('h2', class_='titel')
            if title_elem:
                title = title_elem.text.strip()
            
            # Get the category
            category = ""
            category_elem = news_item_html.find('div', class_='categorie')
            if category_elem and category_elem.find('a'):
                category = category_elem.find('a').text.strip()
            
            # Get reactions info and link
            reactions_info = ""
            reactions_link = None
            reactions = []
            reacties_elem = news_item_html.find('div', class_='reacties-link')
            if reacties_elem:
                reactions_info = reacties_elem.text.strip()
                link = reacties_elem.find('a')
                if link and link.get('href'):
                    reactions_link = f"https://www.waldnet.nl{link.get('href')}"
                    reactions = get_reactions(reactions_link)
            
            # Get article link and image
            article_link = None
            image = None
            article_elem = news_item_html.find('a', class_='nieuws-link')
            if article_elem:
                article_link = f"https://www.waldnet.nl{article_elem.get('href')}"
                img_elem = article_elem.find('img', class_='nieuws-afbeelding')
                if img_elem:
                    image = Image(
                        url=img_elem.get('src'),
                        alt=img_elem.get('alt', '')
                    )
            
            # Create NewsItem object
            news_item = NewsItem(
                title=title,
                category=category,
                reactions_info=reactions_info,
                reactions_link=reactions_link,
                reactions=reactions,
                article_link=article_link,
                image=image
            )
            
            # Print the news item
            print_news_item(news_item)
            
            # Add a small delay between fetching reactions
            time.sleep(1)
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")





