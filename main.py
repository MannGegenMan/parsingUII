import requests
from bs4 import BeautifulSoup
import fake_useragent
import time 
import json

def get_links(text):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=f'https://hh.ru/search/resume?text={text}&area=113&isDefaultArea=true&ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&exp_period=all_time&page=0',
        headers={'user-agent': ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try: 
        page_count = int(soup.find('div', attrs={'class':'pager'}).find_all('span', recursive=False)[-1].find('a').find('span').text)
    except:
        return
    for page in range(page_count):
        try:
            data = requests.get(
                url=f'https://hh.ru/search/resume?text={text}&area=113&isDefaultArea=true&ored_clusters=true&order_by=relevance&search_period=0&logic=normal&pos=full_text&exp_period=all_time&page={page}',
                headers={'user-agent':ua.random}
            )
            if data.status_code != 200:
                continue
            soup = BeautifulSoup(data.content, 'lxml')

            for a in soup.find_all('a', attrs={'class': 'bloko-link'}):
                yield f'https://hh.ru{a.attrs['href'].split('?')[0]}'
        except Exception as e:
            print(f'{e}')
            time.sleep(1)

def get_resume(link):
    ua = fake_useragent.UserAgent()
    data = requests.get(
        url=link,
        headers={'user-agent':ua.random}
    )
    if data.status_code != 200:
        return
    soup = BeautifulSoup(data.content, 'lxml')
    try:
        name = soup.find(attrs={'class':'resume-block__title-text'}).text
    except:
        name = ''
    try:
        salary = soup.find(attrs={'class':'resume-block__salary'}).text.replace('\u2009','').replace('\xa0',' ')
    except:
        salary = ''
    try:
        tags = [tag.text for tag in soup.find(attrs={'class':'bloko-tag-list'}).find_all(attrs={'class':'bloko-tag__section_text'})]
    except: 
        tags = []
    try:
        experience = soup.find(attrs={'class':'resume-block'}).text
    except:
        experience = ''
    try:
        about_me = soup.find(attrs={'class':'resume-block-container'}).text
    except:
        about_me = ''
    resume = {
        'Имя':name,
        'Зарплата':salary,
        'Ключевые навыки':tags,
        'Опыт работы':experience,
        'Обо мне':about_me
    }
    return resume

if __name__ == "__main__":
    data = []
    for a in get_links('python'):
        data.append(get_resume(a))
        time.sleep(1)
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data,f,indent=4,ensure_ascii=False)