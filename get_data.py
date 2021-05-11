import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import json

def get_connections(url: str) -> list:
    references = []
    connections_source_code = requests.get(url)
    connections_soup = BeautifulSoup(connections_source_code.text, 'html.parser')
    references_anchor = connections_soup.find('a', {'id': 'references'})
    is_reference = True
    sibling = references_anchor
    while is_reference and sibling is not None:
        sibling = sibling.find_next_sibling()
        if sibling is not None:
            if sibling.name == 'div':
                reference_anchor = sibling.find('a')
                reference_imdb_title = reference_anchor['href'].replace('/', '').replace('title', '')
                references.append(reference_imdb_title)
            
            elif sibling.name == 'a':
                is_reference = False

    return references

# Remove títulos que não referenciam nenhum e outro título e não são referenciados
def clean_data(titles_df: pd.DataFrame, references_df: pd.DataFrame) -> None:
    for index, title in titles_df['imdb_title'].items():
        if not (references_df['imdb_title'].str.contains(title).any() and references_df['reference_imdb_title'].str.contains(title).any()):
            title_name = titles_df.loc[titles_df['imdb_title'] == title]['title']
            print(f'Removendo {title_name}')
            titles_df.drop(index=index, inplace=True)
 

def main():
    titles_df = pd.DataFrame(columns=['imdb_title', 'title', 'genre'])
    references_df = pd.DataFrame(columns=['imdb_title', 'reference_imdb_title'])

    url = 'https://www.imdb.com/search/title/?count=250&groups=top_1000&sort=user_rating'

    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text, 'html.parser')
    for item_header in tqdm(soup.findAll('h3', {'class': 'lister-item-header'})):
        anchor = item_header.find('a')
        link = anchor['href']
        movie_title = anchor.text
        connections_url = 'https://www.imdb.com' + link + 'movieconnections'
        imdb_title = link.replace('/', '').replace('title', '')

        sibling = item_header.find_next_sibling()
        genre_span = sibling.find('span', {'class': 'genre'})
        genre = genre_span.text.split(',')[0].replace('\n', '')

        titles_df = titles_df.append(
            {'imdb_title': imdb_title, 'title': movie_title, 'genre': genre},
            ignore_index=True
        )

        # Search connections
        references = get_connections(connections_url)
        for reference in references:
            references_df = references_df.append(
                {'imdb_title': imdb_title, 'reference_imdb_title': reference},
                ignore_index=True
            )

    
    for index, value in references_df['reference_imdb_title'].items():
        if not titles_df['imdb_title'].str.contains(value).any():
            references_df.drop(index=index, inplace=True)

    clean_data(titles_df, references_df)
    
    titles_df.to_csv('titles.csv', sep=';', index=False)
    references_df.to_csv('references.csv', sep=';', index=False)



                    








if __name__=="__main__":
    main()
