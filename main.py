import json

import bs4
import fake_headers
import requests
from environs import Env


def main(page_count: int, dollars: bool):
    headers = fake_headers.Headers('chrome', os='mac')
    headers = headers.generate()
    result = []

    for page_num in range(1, page_count + 1):

        params = {
            'text': 'python',
            'area': (1, 2),
            'page': page_num
        }

        response = requests.get('https://spb.hh.ru/search/vacancy', params=params, headers=headers)

        main_html = bs4.BeautifulSoup(response.text, 'lxml')

        vacancies = main_html.find_all('div', class_='vacancy-serp-item__layout')

        for vacancy in vacancies:
            link_to_vacancy = vacancy.find('h3', class_='bloko-header-section-3').find('a')['href']

            if not check_for_keywords(link_to_vacancy, headers):
                continue
            title = vacancy.find('a', class_='serp-item__title').text.replace('\xa0', ' ')
            company = vacancy.find('a', class_='bloko-link bloko-link_kind-tertiary').text.replace('\xa0', ' ')
            city = vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).text.replace('\xa0', ' ')
            salary_block = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            salary = salary_block.text.replace('\xa0', ' ').replace('\u202F', ' ') if salary_block else 'Не указано'
            if dollars and '$' not in salary:
                continue
            vacancy = {
                'title': title.strip(),
                'company': company.strip(),
                'city': city.strip(),
                'salary': salary.strip(),
                'link_to_vacancy': link_to_vacancy.strip()
            }
            result.append(vacancy)

    with open('result.json', 'w') as file:
        json.dump(result, file, indent=2, ensure_ascii=False)


def check_for_keywords(url, headers):
    keywords = ['django', 'flask']

    response = requests.get(url, headers=headers)
    main_html = bs4.BeautifulSoup(response.text, 'lxml')
    description = main_html.find('div', class_='g-user-content').text
    for word in keywords:
        if word in description.lower():
            return True
    return False


if __name__ == '__main__':
    env = Env()
    env.read_env()
    PAGE_COUNT = env.int('PAGE_COUNT')
    ONLY_DOLLARS = env.bool('ONLY_DOLLARS')

    main(PAGE_COUNT, ONLY_DOLLARS)
