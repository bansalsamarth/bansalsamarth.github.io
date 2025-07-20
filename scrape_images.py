#!/usr/bin/env python3

import csv
import os
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import hashlib

def get_cover_image(url, title):
    """Extract cover image from article URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try different methods to find cover image
        image_url = None
        
        # Method 1: OpenGraph image
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            image_url = og_image['content']
        
        # Method 2: Twitter card image
        if not image_url:
            twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
            if twitter_image and twitter_image.get('content'):
                image_url = twitter_image['content']
        
        # Method 3: First image in article content
        if not image_url:
            article_selectors = [
                'article img', '.article img', '.content img', 
                '.post img', '.story img', '.entry img'
            ]
            for selector in article_selectors:
                img = soup.select_one(selector)
                if img and img.get('src'):
                    image_url = img['src']
                    break
        
        # Method 4: Any img with reasonable size attributes
        if not image_url:
            imgs = soup.find_all('img')
            for img in imgs:
                src = img.get('src')
                if src and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'profile']):
                    image_url = src
                    break
        
        if image_url:
            # Make URL absolute
            image_url = urljoin(url, image_url)
            return image_url
            
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return None

def download_image(image_url, filename):
    """Download and save image locally."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(image_url, headers=headers, timeout=15, stream=True)
        response.raise_for_status()
        
        # Check if it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return None
        
        # Save the image
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return filename
        
    except Exception as e:
        print(f"Error downloading {image_url}: {e}")
        return None

def process_journalism_images():
    """Process all journalism articles and fetch their cover images."""
    
    # Paths
    csv_path = '/Users/samarth/personal_website/samarth-blog/journalism_links.csv'
    images_dir = '/Users/samarth/personal_website/samarth-blog/output/assets/journalism-covers'
    
    # Create images directory
    os.makedirs(images_dir, exist_ok=True)
    
    # Load articles
    articles = []
    with open(csv_path, 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row.get('title', '').strip() and row.get('original_url', '').strip():
                articles.append(row)
    
    print(f"Processing {len(articles)} articles...")
    
    updated_articles = []
    
    for i, article in enumerate(articles, 1):
        title = article['title']
        url = article['original_url']
        
        print(f"\n[{i}/{len(articles)}] Processing: {title[:60]}...")
        
        # Create filename based on title hash
        title_hash = hashlib.md5(title.encode()).hexdigest()[:12]
        image_filename = f"{title_hash}.jpg"
        image_path = os.path.join(images_dir, image_filename)
        
        # Skip if image already exists
        if os.path.exists(image_path):
            print(f"  ✓ Image already exists")
            article['cover_image'] = f"/assets/journalism-covers/{image_filename}"
        else:
            # Try to get cover image
            cover_image_url = get_cover_image(url, title)
            
            if cover_image_url:
                print(f"  → Found image: {cover_image_url}")
                downloaded_path = download_image(cover_image_url, image_path)
                
                if downloaded_path:
                    print(f"  ✓ Downloaded successfully")
                    article['cover_image'] = f"/assets/journalism-covers/{image_filename}"
                else:
                    print(f"  ✗ Download failed")
                    article['cover_image'] = ''
            else:
                print(f"  ✗ No cover image found")
                article['cover_image'] = ''
        
        updated_articles.append(article)
        
        # Rate limiting
        time.sleep(1)
    
    # Update CSV with cover image paths
    fieldnames = list(articles[0].keys()) + ['cover_image']
    if 'cover_image' not in fieldnames:
        fieldnames.append('cover_image')
    
    csv_backup_path = csv_path + '.backup'
    os.rename(csv_path, csv_backup_path)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_articles)
    
    print(f"\n✓ Completed! Updated CSV with cover image paths.")
    print(f"✓ Backup saved to: {csv_backup_path}")
    
    # Summary
    with_images = sum(1 for a in updated_articles if a.get('cover_image'))
    print(f"✓ {with_images}/{len(updated_articles)} articles have cover images")

if __name__ == '__main__':
    process_journalism_images()