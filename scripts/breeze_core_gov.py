def extract_bahamasgov_articles(start_page=1, end_page=1):
    import requests
    from bs4 import BeautifulSoup

    articles = []

    for page in range(start_page, end_page + 1):
        url = f'https://www.bahamas.gov.bs/wps/portal/public/gov/government/news?page={page}'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        news_items = soup.find_all('div', class_='news-item')
        for item in news_items:
            title_tag = item.find('h3')
            date_tag = item.find('time')
            summary_tag = item.find('p')

            title = title_tag.get_text(strip=True) if title_tag else 'No Title'
            date = date_tag.get_text(strip=True) if date_tag else 'No Date'
            summary = summary_tag.get_text(strip=True) if summary_tag else 'No Summary'

            articles.append({
                'title': title,
                'date': date,
                'summary': summary
            })

    return articles
