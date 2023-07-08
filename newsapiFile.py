import http.client
import json
import ast
def getTopNewsHeadlines(category):#later maybe can specify whether we want sports headlines/business headlines/entertainment headlines etc.
    url = "newsdata.io"
    endpoint = "/api/1/news"
    params = {
        "apikey": "pub_240986d588933e4c649b81cd9f83b917ec57d",
        "country": "gb",
        "language": "en",
        "category": category
    }

    conn = http.client.HTTPSConnection(url)

    query_params = "&".join([f"{key}={value}" for key, value in params.items()])
    request_url = f"{endpoint}?{query_params}"

    conn.request("GET", request_url)

    response = conn.getresponse()

    data = response.read().decode("utf-8")

    conn.close()

    json_data = json.loads(data)

    headlines = []
    print("Here are the top news headlines")
    #print(json_data)
    for i in json_data["results"]:
        print(i["title"])
        headlines.append(i["title"])
    return headlines
