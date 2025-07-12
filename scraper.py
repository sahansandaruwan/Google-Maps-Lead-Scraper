import time
import random
import csv
import json
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from bs4 import BeautifulSoup

class GoogleMapsLeadScraper:
    def __init__(self, headless=False):
        self.setup_driver(headless)
        self.leads = []
        self.min_delay = 1
        self.max_delay = 3
        
    def setup_driver(self, headless):
        """Setup Chrome driver with human-like settings"""
        chrome_options = Options()
        
        # Human-like browser settings
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        
        # Add user agent to look more human
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        if headless:
            chrome_options.add_argument("--headless")
            
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
    def human_like_delay(self, min_delay=None, max_delay=None):
        """Add random delays to simulate human behavior"""
        if min_delay is None:
            min_delay = self.min_delay
        if max_delay is None:
            max_delay = self.max_delay
        time.sleep(random.uniform(min_delay, max_delay))
        
    def scroll_slowly(self, element=None):
        """Scroll like a human would"""
        if element:
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'});", element)
        else:
            # Scroll down slowly
            for i in range(3):
                self.driver.execute_script(f"window.scrollBy(0, {random.randint(200, 400)});")
                time.sleep(random.uniform(0.5, 1))
                
    def human_like_typing(self, element, text):
        """Type text like a human with natural pauses"""
        element.clear()
        time.sleep(random.uniform(0.5, 1.0))
        
        # Type the actual text with human-like rhythm
        for i, char in enumerate(text):
            element.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))
            
            # Occasional longer pauses
            if random.random() < 0.03:
                time.sleep(random.uniform(0.3, 0.8))
    
    def extract_email_from_text(self, text):
        """Extract email addresses from text"""
        if not text:
            return ""
        
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else ""
    
    def extract_phone_from_text(self, text):
        """Extract phone numbers from text"""
        if not text:
            return ""
        
        # Common phone patterns
        phone_patterns = [
            r'\+?1?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
            r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})',
            r'(\d{3})[-.\s]?(\d{3})[-.\s]?(\d{4})'
        ]
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                if len(matches[0]) == 3:  # Tuple format
                    return f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
                else:
                    return matches[0]
        
        return ""
    
    def search_for_businesses(self, query, location):
        """Search for businesses on Google Maps"""
        try:
            # Go to Google Maps
            self.driver.get("https://www.google.com/maps")
            self.human_like_delay(3, 5)
            
            # Find and click search box
            search_box = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, "searchboxinput"))
            )
            
            # Type search query
            search_query = f"{query} {location}"
            print(f"🔍 Searching for: {search_query}")
            
            self.human_like_typing(search_box, search_query)
            search_box.send_keys(Keys.RETURN)
            
            # Wait for results to load
            self.human_like_delay(5, 8)
            
            return True
            
        except Exception as e:
            print(f"❌ Error in search: {str(e)}")
            return False
    
    def wait_for_results(self):
        """Wait for search results to load"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-result-index]"))
            )
            return True
        except TimeoutException:
            # Try alternative selector
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".hfpxzc"))
                )
                return True
            except TimeoutException:
                print("⚠️ Results took too long to load")
                return False
    
    def get_business_elements(self):
        """Get business listing elements using multiple selectors"""
        business_elements = []
        
        # Try different selectors for business listings
        selectors = [
            "[data-result-index]",
            ".hfpxzc",
            ".Nv2PK",
            ".lI9IFe",
            ".VkpGBb",
            "a[href*='/maps/place/']"
        ]
        
        for selector in selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} businesses with selector: {selector}")
                    business_elements = elements
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {str(e)}")
                continue
        
        return business_elements
    
    def extract_business_info(self, business_element):
        """Extract information from a business element"""
        business_data = {
            'name': '',
            'address': '',
            'phone': '',
            'email': '',
            'website': '',
            'rating': '',
            'reviews': '',
            'category': '',
            'hours': ''
        }
        
        try:
            # Click on business to get details
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", business_element)
            self.human_like_delay(1, 2)
            
            # Click the business
            ActionChains(self.driver).move_to_element(business_element).click().perform()
            self.human_like_delay(4, 6)
            
            # Extract business name
            name_selectors = [
                "h1[data-attrid='title']",
                ".DUwDvf",
                ".x3AX1-LfntMc-header-title-title",
                ".qrShPb",
                ".SPZz6b h1",
                ".fontHeadlineLarge",
                "h1.DUwDvf"
            ]
            
            for selector in name_selectors:
                try:
                    name_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if name_elem and name_elem.text.strip():
                        business_data['name'] = name_elem.text.strip()
                        print(f"📋 Found business: {business_data['name']}")
                        break
                except:
                    continue
            
            # Extract address
            address_selectors = [
                "[data-item-id='address']",
                ".Io6YTe",
                "[data-value='Address']",
                ".rogA2c",
                "[data-item-id='address'] .fontBodyMedium",
                "button[data-item-id='address']"
            ]
            
            for selector in address_selectors:
                try:
                    address_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if address_elem and address_elem.text.strip():
                        business_data['address'] = address_elem.text.strip()
                        print(f"📍 Address: {business_data['address']}")
                        break
                except:
                    continue
            
            # Extract phone number
            phone_selectors = [
                "[data-item-id='phone']",
                "button[data-item-id='phone']",
                ".rogA2c .fontBodyMedium",
                "[data-value='Phone']",
                "a[href^='tel:']"
            ]
            
            for selector in phone_selectors:
                try:
                    phone_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if phone_elem:
                        phone_text = phone_elem.text.strip()
                        if phone_text:
                            business_data['phone'] = phone_text
                            print(f"📞 Phone: {business_data['phone']}")
                            break
                        # Try href for tel links
                        href = phone_elem.get_attribute('href')
                        if href and 'tel:' in href:
                            business_data['phone'] = href.replace('tel:', '')
                            print(f"📞 Phone: {business_data['phone']}")
                            break
                except:
                    continue
            
            # Extract website
            website_selectors = [
                "[data-item-id='authority']",
                "a[data-value='Website']",
                ".CsEnBe a",
                "a[href*='http']:not([href*='google']):not([href*='maps'])",
                "button[data-item-id='authority']"
            ]
            
            for selector in website_selectors:
                try:
                    website_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if website_elem:
                        href = website_elem.get_attribute('href')
                        if href and 'http' in href and 'google' not in href:
                            business_data['website'] = href
                            print(f"🌐 Website: {business_data['website']}")
                            break
                except:
                    continue
            
            # Extract rating
            rating_selectors = [
                ".MW4etd",
                ".ceNzKf",
                "[data-value='Rating']",
                ".fontDisplayLarge"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_elem = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if rating_elem and rating_elem.text.strip():
                        rating_text = rating_elem.text.strip()
                        if any(char.isdigit() for char in rating_text):
                            business_data['rating'] = rating_text
                            print(f"⭐ Rating: {business_data['rating']}")
                            break
                except:
                    continue
            
            # Extract reviews count
            try:
                reviews_elem = self.driver.find_element(By.CSS_SELECTOR, ".UY7F9")
                if reviews_elem:
                    business_data['reviews'] = reviews_elem.text.strip()
                    print(f"📝 Reviews: {business_data['reviews']}")
            except:
                pass
            
            # Extract category
            try:
                category_elem = self.driver.find_element(By.CSS_SELECTOR, ".DkEaL")
                if category_elem:
                    business_data['category'] = category_elem.text.strip()
                    print(f"🏷️ Category: {business_data['category']}")
            except:
                pass
            
            # Look for email in page source or text
            try:
                page_source = self.driver.page_source
                email = self.extract_email_from_text(page_source)
                if email:
                    business_data['email'] = email
                    print(f"📧 Email: {business_data['email']}")
            except:
                pass
            
            # Try to get more info from website if available
            if business_data['website'] and not business_data['email']:
                try:
                    self.extract_info_from_website(business_data)
                except:
                    pass
            
            # Go back to results
            self.driver.back()
            self.human_like_delay(2, 4)
            
            return business_data
            
        except Exception as e:
            print(f"❌ Error extracting business info: {str(e)}")
            # Try to go back if we're stuck
            try:
                self.driver.back()
                self.human_like_delay(1, 2)
            except:
                pass
            return business_data
    
    def extract_info_from_website(self, business_data):
        """Try to extract additional info from business website"""
        try:
            if not business_data['website']:
                return
            
            # Open website in new tab
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[1])
            
            self.driver.get(business_data['website'])
            time.sleep(3)
            
            # Look for email on website
            page_source = self.driver.page_source
            email = self.extract_email_from_text(page_source)
            if email and not business_data['email']:
                business_data['email'] = email
                print(f"📧 Email from website: {email}")
            
            # Look for phone on website if not found
            if not business_data['phone']:
                phone = self.extract_phone_from_text(page_source)
                if phone:
                    business_data['phone'] = phone
                    print(f"📞 Phone from website: {phone}")
            
            # Close tab and switch back
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        except Exception as e:
            print(f"❌ Error extracting from website: {str(e)}")
            # Make sure we're back on the main tab
            try:
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
    
    def scrape_leads(self, query, location, max_results=50):
        """Main scraping function"""
        print(f"🚀 Starting lead scraping for '{query}' in '{location}'")
        
        # Search for businesses
        if not self.search_for_businesses(query, location):
            return []
        
        # Wait for results
        if not self.wait_for_results():
            return []
        
        # Get business elements
        business_elements = self.get_business_elements()
        
        if not business_elements:
            print("❌ No business listings found")
            return []
        
        print(f"🎯 Found {len(business_elements)} businesses to scrape")
        
        # Scrape each business
        scraped_count = 0
        for i, business_element in enumerate(business_elements):
            if scraped_count >= max_results:
                break
            
            print(f"\n🔍 Scraping business {scraped_count + 1}/{min(max_results, len(business_elements))}")
            
            try:
                business_data = self.extract_business_info(business_element)
                
                # Only add if we got essential info
                if business_data['name'] and (business_data['address'] or business_data['phone']):
                    self.leads.append(business_data)
                    scraped_count += 1
                    print(f"✅ Successfully scraped: {business_data['name']}")
                else:
                    print(f"⚠️ Skipped business - insufficient data")
                
                # Human-like delay between businesses
                self.human_like_delay(2, 4)
                
                # Scroll to load more results if needed
                if scraped_count < max_results and i % 5 == 0:
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)
                
            except Exception as e:
                print(f"❌ Error scraping business {i+1}: {str(e)}")
                continue
        
        print(f"\n✅ Scraping completed! Found {len(self.leads)} valid leads")
        return self.leads
    
    def save_to_csv(self, filename="google_maps_leads.csv"):
        """Save leads to CSV file"""
        if not self.leads:
            print("❌ No leads to save")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['name', 'address', 'phone', 'email', 'website', 'rating', 'reviews', 'category', 'hours']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for lead in self.leads:
                    writer.writerow(lead)
            
            print(f"✅ Saved {len(self.leads)} leads to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving CSV: {str(e)}")
            return False
    
    def save_to_json(self, filename="google_maps_leads.json"):
        """Save leads to JSON file"""
        if not self.leads:
            print("❌ No leads to save")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as jsonfile:
                json.dump(self.leads, jsonfile, indent=2, ensure_ascii=False)
            
            print(f"✅ Saved {len(self.leads)} leads to {filename}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving JSON: {str(e)}")
            return False
    
    def close(self):
        """Close the browser"""
        try:
            self.driver.quit()
        except:
            pass

def get_user_input():
    """Get customized input from user"""
    print("=" * 60)
    print("🗺️  GOOGLE MAPS LEAD SCRAPER")
    print("=" * 60)
    
    # Business type/query
    print("\n📋 SEARCH CONFIGURATION")
    print("-" * 30)
    query = input("Enter business type (e.g., restaurants, dentists, plumbers): ").strip()
    if not query:
        query = "restaurants"
    
    # Location
    location = input("Enter location (e.g., New York, NY / Los Angeles, CA): ").strip()
    if not location:
        location = "New York, NY"
    
    # Number of results
    while True:
        try:
            max_results = int(input("How many leads do you want? (1-100): ") or "20")
            if 1 <= max_results <= 100:
                break
            else:
                print("Please enter a number between 1 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Browser mode
    print("\n🖥️  BROWSER SETTINGS")
    print("-" * 30)
    print("1. Visible browser (you can see what's happening)")
    print("2. Headless mode (faster, runs in background)")
    
    while True:
        browser_choice = input("Choose browser mode (1 or 2): ").strip() or "1"
        if browser_choice in ['1', '2']:
            headless = browser_choice == '2'
            break
        else:
            print("Please enter 1 or 2")
    
    # File naming
    print("\n💾 OUTPUT SETTINGS")
    print("-" * 30)
    
    default_filename = f"{query.replace(' ', '_')}_{location.replace(' ', '_').replace(',', '')}_leads"
    custom_filename = input(f"Enter filename (default: {default_filename}): ").strip()
    
    if not custom_filename:
        custom_filename = default_filename
    
    # File format
    print("\n📁 Choose output format:")
    print("1. CSV only")
    print("2. JSON only") 
    print("3. Both CSV and JSON")
    
    while True:
        format_choice = input("Choose format (1, 2, or 3): ").strip() or "3"
        if format_choice in ['1', '2', '3']:
            break
        else:
            print("Please enter 1, 2, or 3")
    
    return {
        'query': query,
        'location': location,
        'max_results': max_results,
        'headless': headless,
        'filename': custom_filename,
        'format_choice': format_choice
    }

def display_summary(leads, config):
    """Display summary of scraped leads"""
    print("\n" + "=" * 60)
    print("📊 SCRAPING SUMMARY")
    print("=" * 60)
    print(f"Search Query: {config['query']}")
    print(f"Location: {config['location']}")
    print(f"Total Leads Found: {len(leads)}")
    
    if leads:
        print(f"\n🔝 SAMPLE RESULTS:")
        print("-" * 40)
        
        for i, lead in enumerate(leads[:3], 1):
            print(f"\n{i}. {lead['name']}")
            if lead['address']:
                print(f"   📍 Address: {lead['address']}")
            if lead['phone']:
                print(f"   📞 Phone: {lead['phone']}")
            if lead['email']:
                print(f"   📧 Email: {lead['email']}")
            if lead['website']:
                print(f"   🌐 Website: {lead['website']}")
            if lead['rating']:
                print(f"   ⭐ Rating: {lead['rating']}")
            if lead['category']:
                print(f"   🏷️ Category: {lead['category']}")
    
    print(f"\n💾 Files saved with name: {config['filename']}")

# Main execution
if __name__ == "__main__":
    scraper = None
    try:
        # Get user configuration
        config = get_user_input()
        
        print(f"\n🚀 Starting scraper...")
        print(f"Searching for: {config['query']}")
        print(f"Location: {config['location']}")
        print(f"Target results: {config['max_results']}")
        
        # Initialize scraper
        scraper = GoogleMapsLeadScraper(headless=config['headless'])
        
        # Scrape leads
        leads = scraper.scrape_leads(
            config['query'], 
            config['location'], 
            config['max_results']
        )
        
        if leads:
            # Save results based on format choice
            if config['format_choice'] in ['1', '3']:  # CSV
                scraper.save_to_csv(f"{config['filename']}.csv")
                
            if config['format_choice'] in ['2', '3']:  # JSON
                scraper.save_to_json(f"{config['filename']}.json")
            
            # Display summary
            display_summary(leads, config)
        else:
            print("❌ No leads were scraped. Please try different search terms or location.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        if scraper:
            scraper.close()
        
        print("\n✅ Scraping session completed!")
        input("Press Enter to exit...")
