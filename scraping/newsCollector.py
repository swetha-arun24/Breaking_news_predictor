import requests
from model import predict_news_category
from db.retrival import save_in_es,get_breaking_news,del_old_news
def news_collect():
    url = ('https://newsapi.org/v2/top-headlines?country=us&apiKey=giveyour_api_key')

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Error: Failed to fetch news sources. Status code {response.status_code}")
        return []

    NEWS_RESPONSE = response.json()

    if "articles" not in NEWS_RESPONSE:
        print("Error: No sources found in response.")
        return []
    print(NEWS_RESPONSE["totalResults"])
    filtered_sources = []
    breaking_news_count = 0
    non_breaking_news_count = 0
    for article in NEWS_RESPONSE["articles"]:
        description = article.get("description", "")  # Get the description (default to empty string if None)
        title = article.get("title","")
        text_to_predict = description if description else title
        if text_to_predict:  # Process only if description is not None
            # print(f"Processing article: {text_to_predict}")
            try:
                # Predict the category of the description
                prediction = predict_news_category(text_to_predict)  # Assume predict_news_category is defined
            except RecursionError:
                print("Error: Recursion occurred in predict_news_category")
                continue  # Skip to the next article
            
            print(f"Prediction result: {prediction}")

            # Count and filter based on prediction
            if prediction == "Breaking_News":
                breaking_news_count += 1
                filtered_sources.append(article)
            elif prediction == "Non_Breaking_News":
                non_breaking_news_count += 1

    print(f"breaking news {breaking_news_count} and non breaking news {non_breaking_news_count}")
    
    save_in_es(filtered_sources)
    
    del_old_news()
    return "saved"
