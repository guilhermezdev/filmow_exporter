import argparse
import requests
import sys
from bs4 import BeautifulSoup
from alive_progress import alive_bar

class FilmowParser:
    def __init__(self, username):
        self.username = username
        self.base_url = f'https://filmow.com/usuario/{username}/filmes/ja-vi/'
        self.movies = []

    def get_last_page(self):
        page = requests.get(self.base_url)
        soup = BeautifulSoup(page.content, 'html.parser')
        pagination_finder = soup.find('div', class_='pagination').find_all('a')
        last_page_finder = pagination_finder[-1]

        return int(last_page_finder['href'].split('pagina=')[-1])

    def get_movies(self):
        with alive_bar(title='Fetching your movie list') as bar:
            for i in range(self.get_last_page()):
                page = requests.get(f'{self.base_url}?pagina={i+1}')
                soup = BeautifulSoup(page.content, 'html.parser')
                movies_raw = soup.find_all('li', class_='movie_list_item')

                for movie in movies_raw:
                        movie_action = movie.find('a', class_='tip-movie')
                        self.movies.append({
                            'name': movie_action['title'],
                            'key': movie_action['data-movie-pk']
                        })
                        bar()

        with alive_bar(len(self.movies), title='Fetching the original titles of movies') as bar:
            for movie in self.movies:
                original_name = self.get_movie_original_name(movie['key'])
                if original_name is not None:
                    movie['name'] = original_name
                bar()

    def get_movie_original_name(self, movie_key):
        url = f'https://filmow.com/async/tooltip/movie/?movie_pk={movie_key}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['movie']['title_orig']
        else:
            print(f"Error fetching movie original name: {response.status_code}")
            return None

    def dump_movies(self):
        with open('filmow_ja_vi.csv', 'w', encoding='utf8') as f:
            f.write('Title\n')
            for movie in self.movies:
                f.write(f"{movie['name']}\n")

    def parse(self):
        self.get_movies()
        self.dump_movies()

def main():
    parser = argparse.ArgumentParser(prog='FilmowExporter' ,description='Export Filmow movies already watched movies to a CSV file readable by Letterboxd')
    parser.add_argument('username', type=str, help='Filmow username')
    args = parser.parse_args()

    filmow_parser = FilmowParser(args.username)
    filmow_parser.parse()

if __name__ == '__main__':
    sys.exit(main())  
