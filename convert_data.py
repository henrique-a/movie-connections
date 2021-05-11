import pandas as pd
import json

def main():
    references_df = pd.read_csv('references.csv', sep=';')
    titles_df = pd.read_csv('titles.csv', sep=';')
    hierarchical = []
    for index, movie in titles_df.iterrows():
        
        references = references_df[references_df['imdb_title'] == movie.imdb_title]['reference_imdb_title'].values
        imports = []
        for reference in references:
            reference_info = titles_df[titles_df['imdb_title'] == reference]
            title = reference_info.title.values[0]
            genre = reference_info.genre.values[0]
            imports.append('genre.' + genre + '.' + title)  
        

        hierarchical.append({
            'name': 'genre.' + movie.genre + '.' + movie.title,
            'imports': imports
        })

    with open('movie_connections.json', 'w', encoding='utf-8') as fp:
        json.dump(hierarchical, fp, ensure_ascii=False)



if __name__=="__main__":
    main()



