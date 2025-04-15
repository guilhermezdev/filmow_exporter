import requests
from bs4 import BeautifulSoup

username = 'guigzp'
base_url = f'https://filmow.com/usuario/{username}/filmes/ja-vi/'

page = requests.get(base_url)
soup = BeautifulSoup(page.content, 'html.parser')

movies = []

pagination_finder = soup.find('div', class_='pagination').find_all('a')
last_page_finder = pagination_finder[-1]
last_page = int(last_page_finder['href'].split('pagina=')[-1])

for i in range(last_page):
    page = requests.get(f'{base_url}?pagina={i+1}')
    soup = BeautifulSoup(page.content, 'html.parser')
    movies_raw = soup.find_all('li', class_='movie_list_item')
    for movie in movies_raw:
        movie_key = movie['data-movie-pk']
        movie_action = movie.find('a', class_='tip-movie')
        movie_url = movie_action['href']
        movies.append({
            'key': movie_key,
            'name': movie_action['title'],
            'url': f'https://filmow.com/{movie_url}',
        })

print(movies)