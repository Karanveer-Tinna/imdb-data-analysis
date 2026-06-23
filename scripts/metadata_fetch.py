import requests
import pandas as pd
import socket

# Replace with your own TMDB API key
API_KEY = "YOUR_TMDB_API_KEY_HERE"

list_of_series_names = list(pd.read_csv("../data/series_names.csv")["series_name"])
url = f"https://api.themoviedb.org/3/search/tv"

params = {
    "api_key":API_KEY,
}

data = []
session = requests.Session()

for series_name in list_of_series_names:
    params["query"] = series_name

    try:
        response = session.get(
            url,
            params=params,
            timeout=(5, 5)
        )

    except requests.exceptions.ConnectionError:
        session.close()
        session = requests.Session()
        continue
        
    search_results = response.json()

    if search_results["results"]:
        series_data = search_results["results"][0]
        
        tmdb_id = series_data["id"]
        genre_ids = series_data["genre_ids"]
        description = series_data["overview"]
        origin_country = series_data["origin_country"]
        original_language = series_data["original_language"]
        air_date = series_data["first_air_date"]

        data.append({
            "series_name": series_name,
            "tmdb_id": tmdb_id,
            "genre_ids": genre_ids,
            "origin_country": origin_country,
            "original_language": original_language,
            "first_air_date": air_date,
            "overview": description
        })
    else:
        print(f"No results for {series_name}")

df = pd.DataFrame(data)
print(df)
url = f"https://api.themoviedb.org/3/genre/tv/list"

response = session.get(
    url,
    params={"api_key": API_KEY}
)

genre_dict = {
    g["id"]: g["name"]
    for g in response.json()["genres"]
}

genres = df["genre_ids"].apply(
    lambda ids: [genre_dict[i] for i in ids]
)

df.insert(3, "genres", genres)

all_keywords = []

for tmdb_id in df["tmdb_id"]:
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/keywords"

    response = session.get(
        url,
        params={"api_key": API_KEY}
    )

    keywords = [
        x["name"]
        for x in response.json()["results"]
    ]

    all_keywords.append(keywords)

df["keywords"] = all_keywords

old_df = pd.read_csv("../data/series_metadata.csv")
existing_ids = set(old_df["tmdb_id"])

for row in df.itertuples(index=False):
    if row.tmdb_id not in existing_ids:
        old_df.loc[len(old_df)] = row
        existing_ids.add(row.tmdb_id)

old_df.to_csv("metadata.csv", index=False)