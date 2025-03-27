import requests
from bs4 import BeautifulSoup
import time

NEWS_PAGE = "https://www.waldnet.nl/nieuws.php"

# Define headers to mimic a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

def get_reactions(reactions_url):
    """Fetch and parse reactions from a reactions page."""
    try:
        response = requests.get(reactions_url, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        reactions = []
        # Find all reaction divs
        for reactie_div in soup.find_all('div', class_='reactie'):
            reaction = {}
            
            # Get user info
            user_nickname = reactie_div.find('div', class_='usernickname')
            if user_nickname:
                user_span = user_nickname.find('span')
                if user_span:
                    reaction['user'] = user_span.text.strip()
            
            # Get reaction text
            text_p = reactie_div.find('p')
            if text_p:
                reaction['text'] = text_p.text.strip()
            
            # Get likes
            date_div = reactie_div.find_next('div', class_='reaksje_datum')
            if date_div:
                like_count = date_div.find('span', class_='like-count')
                if like_count:
                    reaction['likes'] = like_count.text.strip()
            
            # Get nested reactions if any
            nested_div = reactie_div.find_next('div', class_='geneste-reacties')
            if nested_div:
                nested_reactions = []
                for nested_reactie in nested_div.find_all('div', class_='reactie'):
                    nested_reaction = {}
                    nested_text = nested_reactie.find('p')
                    if nested_text:
                        nested_reaction['text'] = nested_text.text.strip()
                    nested_reactions.append(nested_reaction)
                reaction['nested_reactions'] = nested_reactions
            
            reactions.append(reaction)
        
        return reactions
    except Exception as e:
        print(f"Error fetching reactions: {e}")
        return []

try:
    # Fetch the page content with headers
    print("Fetching news page...")
    response = requests.get(NEWS_PAGE, headers=headers)
    response.encoding = 'utf-8'
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('div', class_='nieuws-item')
        
        for i, news_item in enumerate(news_items[:10]):
            print(f"\nNews item {i+1}:")
            
            # Get the title
            title = news_item.find('h2', class_='titel')
            if title:
                print(f"Title: {title.text.strip()}")
            
            # Get the category
            category = news_item.find('div', class_='categorie')
            if category:
                category_link = category.find('a')
                if category_link:
                    print(f"Category: {category_link.text.strip()}")
            
            # Get the reactions information and fetch reactions
            reacties = news_item.find('div', class_='reacties-link')
            if reacties:
                print(f"Reactions info: {reacties.text.strip()}")
                link = reacties.find('a')
                if link:
                    href = link.get('href')
                    reactions_url = f"https://www.waldnet.nl{href}"
                    print(f"Reactions link: {reactions_url}")
                    
                    # Fetch and print reactions
                    print("\nReactions:")
                    reactions = get_reactions(reactions_url)
                    for j, reaction in enumerate(reactions, 1):
                        print(f"\nReaction {j}:")
                        print(f"User: {reaction.get('user', 'Unknown')}")
                        print(f"Text: {reaction.get('text', '')}")
                        print(f"Likes: {reaction.get('likes', '0')}")
                        
                        # Print nested reactions if any
                        if 'nested_reactions' in reaction:
                            print("\nNested reactions:")
                            for k, nested in enumerate(reaction['nested_reactions'], 1):
                                print(f"  {k}. {nested.get('text', '')}")
                    
                    # Add a small delay between requests to be nice to the server
                    time.sleep(1)
            
            # Get the article link and image
            article_link = news_item.find('a', class_='nieuws-link')
            if article_link:
                href = article_link.get('href')
                print(f"Article link: https://www.waldnet.nl{href}")
                
                img = article_link.find('img', class_='nieuws-afbeelding')
                if img:
                    print(f"Image: {img.get('src')}")
                    print(f"Image alt: {img.get('alt')}")
            
            print("-" * 50)
    else:
        print(f"Failed to fetch page. Status code: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")





