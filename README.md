
<div align="center">
  <img src="https://sandaruwan-img-host.pages.dev/Google_Maps_Lead_Scraper-removebg-preview.png" width="350" height="350">
  
  <h1> 🗺️ Google Maps Lead Scraper </h1>
</div>



![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Selenium](https://img.shields.io/badge/Selenium-Automation-green.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)

> 💼 Extract real-time business leads (name, phone, email, address, website, rating, etc.) directly from **Google Maps** using human-like automation powered by Selenium.

---

## ✨ Features

- 🔍 **Search by business type & location**
- 🤖 Human-like behavior (typing, scrolling, delays)
- 📥 Extracts:
  - Business name
  - Address
  - Phone number
  - Email (including from website)
  - Website URL
  - Rating & reviews
  - Business category
- 🧠 Intelligent fallbacks for multiple selectors
- 📂 Export results as **CSV**, **JSON**, or both
- 🧪 Supports **headless** and visible browser modes
- 💾 Autosaves results on success

---

## 🚀 Getting Started

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/google-maps-lead-scraper.git
cd google-maps-lead-scraper
````

### 2. Install Dependencies

Ensure you have **Python 3.8+** and **Google Chrome** installed.

```bash
pip install -r requirements.txt
```

> ✨ Required packages include:
>
> * `selenium`
> * `beautifulsoup4`
> * `requests`

### 3. Run the Scraper

```bash
python scraper.py
```

---

## 🧑‍💻 Usage Example

```text
Enter business type (e.g., restaurants): dentists
Enter location (e.g., New York, NY): San Francisco, CA
How many leads do you want? (1-100): 20
Choose browser mode (1 = visible, 2 = headless): 1
Enter filename (default: dentists_SanFrancisco_leads): 
Choose format (1 = CSV, 2 = JSON, 3 = Both): 3
```

✅ Leads will be saved to:

* `dentists_SanFrancisco_leads.csv`
* `dentists_SanFrancisco_leads.json`

---

## 📁 Output Sample (JSON)

```json
[
  {
    "name": "Smile Dental Group",
    "address": "1234 Mission St, San Francisco, CA",
    "phone": "(415) 123-4567",
    "email": "info@smiledental.com",
    "website": "https://smiledental.com",
    "rating": "4.8",
    "reviews": "87",
    "category": "Dentist",
    "hours": "Mon-Fri 9am-5pm"
  }
]
```

---

## 🛠 Tech Stack

* 🐍 Python 3.8+
* 🧭 Selenium WebDriver
* 💡 BeautifulSoup4
* 🌐 Google Chrome
* 🧪 CSV / JSON / Regex

---

## ⚠️ Disclaimer

> This project is intended for **educational purposes** only.
> Scraping Google Maps may violate [Google’s Terms of Service](https://policies.google.com/terms).
> Use responsibly and ethically.

---

## 📌 To-Do

* [ ] Add pagination for large search results
* [ ] Proxy support for IP rotation
* [ ] Autosave progress on crash
* [ ] GUI version using PyQt or Tkinter

---

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first
to discuss what you would like to change.

--- 

## 👨‍💻 Developer

<div align="center">


| [![Sahan Sandaruwan](https://github.com/sahansandaruwan.png?size=150)](https://github.com/sahansandaruwan) | 
|----
 [Sahan Sandaruwan](https://github.com/sahansandaruwan) |
 Developer |
 
 </div>
