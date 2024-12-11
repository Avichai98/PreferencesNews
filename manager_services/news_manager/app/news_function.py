import os
from newsdataapi import NewsDataApiClient
import google.generativeai as genai


def news_data_api(categories, language):
    if len(categories) > 1:
        query_string = " OR ".join(categories)
    else:
        query_string = categories[0]
    news_data_api_key = os.getenv("NEWS_API_KEY")
    api = NewsDataApiClient(apikey=news_data_api_key)
    response_news = api.latest_api(qInTitle=query_string, language=language)
    print(query_string)
    print(response_news)
    return response_news


def gemini_api(response_news):
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
    response_ai_api = model.generate_content(f"""
        {response_news}

        Please format the information as follows:

        Title: [Title of the news article]
        Summary: [A brief sentence summarizing the news]
        Link: [Link to the news article]

        **Additional notes:**
        * Ignore any information that is not relevant to the title, summary, and link.
        * If there are multiple categories, choose all categories. 
        * If there are multiple subheadings, choose the main headline.
        * If there is no explicit summary, write a brief one based on the content.

        **Example:**
        Title: Scientists discover new planet
        Summary: A team of astronomers has discovered an Earth-like planet outside our solar system.
        Link: https://www.space.com/new-planet-discovered
    """)
    return response_ai_api
