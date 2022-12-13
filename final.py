#########################################
##### Name:  Muyang Liu             #####
##### Uniqname:   terryliu          #####
#########################################
import json
import requests
from lxml import etree
from flask import Flask, render_template, request
# import random

app = Flask(__name__)

class Vertex:
    def __init__(self, key):
        self.id = key
        self.connectedTo = {}
        self.review = 'Unknown'
        self.discount = 'Unknown'
        self.image = ''
        self.original_price = 0
        self.current_price = 0
        self.url = ''

    def addNeighbor(self, nbr, weight=0):
        self.connectedTo[nbr] = weight
    def setReview(self,x):
        self.review = x
    def setDiscount(self,x):
        self.discount = x
    def setImage(self,x):
        self.image = x
    def setOriginal(self,x):
        self.original_price = x
    def setCurrent(self,x):
        self.current_price = x
    def setURL(self,x):
        self.url = x

    def getDiscount(self):
        return self.discount
    def getReview(self):
        return self.review
    def getImage(self):
        return self.image
    def getOriginal(self):
        return self.original_price
    def getCurrent(self):
        return self.current_price
    def getURL(self):
        return self.url
    def getId(self):
        return self.id
    def getWeight(self, nbr):
        return self.connectedTo(nbr)
    def getConnections(self):
        return self.connectedTo.keys()

    def __str__(self):
        return str(self.id) + ' connectedTo: ' + str([x.id for x in self.connectedTo])

class Graph:
    def __init__(self):
      self.vertList = {}
      self.numVertices = 0

    def addVertex(self, v):
      self.numVertices += 1
      vertex = Vertex(v)
      self.vertList[v] = vertex
      return vertex

    def getVertex(self, n):
      if n in self.vertList:
        return self.vertList[n]
      else:
        return None

    def __contains__(self):
      return self.vertList.items()

    def addEdge(self, f, t, weight=0):
      if f not in self.vertList:
        self.addVertex(f)
      if t not in self.vertList:
        self.addVertex(t)
      self.vertList[f].addNeighbor(self.vertList[t], weight)

    def getVertices(self):
      return self.vertList.keys()

    def __iter__(self):
      return iter(self.vertList.values())

    def getList(self):
        return self.vertList

    def getnum(self):
        return self.numVertices

def open_cache(filename):
    ''' opens the cache file if it exists and loads the JSON into
    the FIB_CACHE dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(filename, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        # print(cache_dict)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict, filename):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache_dict: dict
    The dictionary to save
    Returns
    -------
    None
    '''
    # print(cache_dict)
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(filename,"w")
    fw.write(dumped_json_cache)
    fw.close()

def fetch_steam_data(headers):
    """This function is to retrieve games data from Steam platform, parse the retrived html files and group them into
    dictionaries. Caching technique is used.
    ----------
    Parameters
    headers: dict
    -------
    Return
    dict: dict, which contains grouped necessary game info.
    """
    steam_dict = open_cache('steam.json')
    if steam_dict:
        return steam_dict
    else:
        dict = {}
        steam_base_url = "https://store.steampowered.com/search/?specials=1&page="
        for i in range(300):
            url = steam_base_url + str(i+1)
            response = requests.get(url, headers=headers)
            html = etree.HTML(response.text)
            game_urls = html.xpath('//div[@id="search_resultsRows"]//a/@href')
            image_urls = html.xpath('//div[@class="col search_capsule"]//img/@src')
            table = html.xpath('//div[@class="responsive_search_name_combined"]')
            # print(image_urls)
            # print(game_urls)
            key = 'page ' + str(i)
            temp = []
            app_cnt = 0
            for j in table:
                # print(j.xpath("//a/@href"))
                # print(j)
                # print(j)
                game_url = game_urls[app_cnt]
                game_image = image_urls[app_cnt]
                game_title = j.xpath('.//span[@class="title"]/text()')[0]
                game_release_date = j.xpath('.//div[@class="col search_released responsive_secondrow"]/text()')
                # print(game_title)
                # print(game_release_date)
                # try:
                game_review_sum = j.xpath('.//span[@class="search_review_summary positive"]/@data-tooltip-html')
                # print(game_review_sum)
                if len(j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')) == 0:
                    game_original_price = 'NaN'
                    game_current_price = 'NaN'
                    game_discount = '-0%'
                else:
                    game_discount = j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')[0]
                    game_original_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/span/strike/text()')[0]
                    game_current_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/text()')[1].strip()

                # except:
                #     print(j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()'))

                # temp.append({'title': game_title, 'discount': game_discount, 'original Price': game_original_price, 'current Price': game_current_price})
                # print(game_title, game_url)
                temp.append({'title': game_title, 'url': game_url, 'image': game_image, 'release_date': game_release_date,\
                            'review_sum': game_review_sum, 'discount': game_discount, 'original Price': game_original_price, 'current Price': game_current_price})
                app_cnt += 1
            # print(temp)
            dict[key] = temp
        save_cache(dict, 'steam.json')
        # print(dict)
        return dict

def search_game(headers, term):
    """This function is to search instant games data on Steam based on the input term. It will return top 3 search results.
    ----------
    Parameters
    headers: dict
    term: str, search term
    -------
    Return
    temp: list, list of top 3 games info.
    """
    url = f"https://store.steampowered.com/search/?term={term}"
    response = requests.get(url, headers=headers)
    html = etree.HTML(response.text)
    try:
        game_urls = html.xpath('//div[@id="search_resultsRows"]//a/@href')
        image_urls = html.xpath('//div[@class="col search_capsule"]//img/@src')
        table = html.xpath('//div[@class="responsive_search_name_combined"]')
        temp = []
        app_cnt = 0
        for j in table:
            if app_cnt == 3:
                break
            game_url = game_urls[app_cnt]
            game_image = image_urls[app_cnt]
            game_title = j.xpath('.//span[@class="title"]/text()')[0]
            game_release_date = j.xpath('.//div[@class="col search_released responsive_secondrow"]/text()')
            game_review_sum = j.xpath('.//span[@class="search_review_summary positive"]/@data-tooltip-html')
            # print(game_review_sum)
            if len(j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')) == 0:
                game_original_price = 'NaN'
                game_current_price = 'NaN'
                game_discount = '-0%'
            else:
                game_discount = j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')[0]
                game_original_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/span/strike/text()')[0]
                game_current_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/text()')[1].strip()
            temp.append({'title': game_title, 'url': game_url, 'image': game_image, 'release_date': game_release_date,\
                        'review_sum': game_review_sum, 'discount': game_discount, 'original Price': game_original_price, 'current Price': game_current_price})
            app_cnt += 1
        # print(dict)
        return temp
    except:
        return []


def fetch_epic_data(headers):
    """This function is to retrieve weekly free games data from Epic platform and then group them into
    dictionaries
    ----------
    Parameters
    headers: dict
    -------
    Return
    dicts: dict, which contains grouped necessary game info.
    """
    epic_base_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?"
    data = {'locale': 'en-US', 'country': 'US', 'allowCountries': 'US'}
    response = requests.get(epic_base_url, headers=headers, params=data)
    a = json.loads(response.text)
    dicts = a['data']['Catalog']['searchStore']
    return dicts

def load_graph(dict):
    """This function is to load Steam games data into 10 categories based on review grades and discounts. 10 categories mean 10 graphs, and for each graph
    there's a major node which connects to every other game nodes of its kind. Therefore there's also a list to store major nodes.
    ----------
    Parameters
    dict: dict, which contains games info retrieved from Steam.
    -------
    Return
    graph_list: list, which contains 10 graphs of games of different categories.
    major_node_list: list, which contains 10 major game nodes.
    """
    page_cnt = 0
    game_list = []
    graph_list = []
    for i in range(10):
        game_list.append([])
        graph_list.append(Graph())

    while page_cnt < 300:
        for i in dict[f'page {page_cnt}']:
            try:
                review_word = i['review_sum'][0].split(' ')[0]
                discount = int(i['discount'].replace('-', '').replace('%', ''))
                if review_word == 'Overwhelmingly':
                    if discount > 66:
                        game_list[0].append(i)
                        tmp = graph_list[0].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    elif discount > 33:
                        game_list[1].append(i)
                        tmp = graph_list[1].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    else:
                        game_list[2].append(i)
                        tmp = graph_list[2].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                elif review_word == 'Very':
                    if discount > 66:
                        game_list[3].append(i)
                        tmp = graph_list[3].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    elif discount > 33:
                        game_list[4].append(i)
                        tmp = graph_list[4].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    else:
                        game_list[5].append(i)
                        tmp = graph_list[5].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                else:
                    if discount > 66:
                        game_list[6].append(i)
                        tmp = graph_list[6].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    elif discount > 33:
                        game_list[7].append(i)
                        tmp = graph_list[7].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
                    else:
                        game_list[8].append(i)
                        tmp = graph_list[8].addVertex(i['title'])
                        tmp.setReview(i['review_sum'][0].replace('<br>', ' '))
                        tmp.setDiscount(i['discount'])
                        tmp.setImage(i['image'])
                        tmp.setOriginal(i['original Price'])
                        tmp.setCurrent(i['current Price'])
                        tmp.setURL(i['url'])
            except:
                game_list[9].append(i)
                tmp = graph_list[9].addVertex(i['title'])
                # tmp.setReview(i['review_sum'][0])
                tmp.setDiscount(i['discount'])
                tmp.setImage(i['image'])
                tmp.setOriginal(i['original Price'])
                tmp.setCurrent(i['current Price'])
                tmp.setURL(i['url'])
        page_cnt += 1

    for j in range(len(game_list)):
        for i in range(1, len(game_list[j])):
            graph_list[j].addEdge(game_list[j][0]['title'], game_list[j][i]['title'], weight=1)
            graph_list[j].addEdge(game_list[j][i]['title'], game_list[j][0]['title'], weight=1)

    major_node_list = []
    for i in game_list:
        major_node_list.append(i[0]['title'])
    return graph_list, major_node_list

review = ''
discount = ''

@app.route('/')
def index():
    """default Flask page
    ------------------
    Return
    redered Flask page using template "index.html"
    """
    return render_template('index.html')

@app.route('/games_details', methods=['POST'])
def show_games():
    """Flask page that shows game infos based on user's preferences
    ------------------
    Return
    redered Flask page using template "game_rec.html"
    """
    headers = {"user-agent": "Mozilla/5.0"}
    steam_dict = fetch_steam_data(headers)
    epic_dict = fetch_epic_data(headers)
    graph_list = []
    major_node_list = []
    graph_list, major_node_list= load_graph(steam_dict)
    global review
    global discount
    review = request.form['reviews']
    discount = request.form['discount']

    info = []
    for i in range(3):
        info.append([])
    if review == "m":
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[4], major_node_list[8]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
        elif discount == "B":
            rdm = [major_node_list[1], major_node_list[4], major_node_list[6]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
        else:
            rdm = [major_node_list[0], major_node_list[3], major_node_list[6]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
    elif review == 'v':
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[1], major_node_list[3]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
        elif discount == "B":
            rdm = [major_node_list[1], major_node_list[3], major_node_list[4]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
        else:
            rdm = [major_node_list[3], list(graph_list[3].getVertex(major_node_list[3]).getConnections())[10].getId(), list(graph_list[3].getVertex(major_node_list[3]).getConnections())[5].getId()]
            for i in range(len(rdm)):
                info[i].append(graph_list[3].getVertex(rdm[i]).getId())
                info[i].append(graph_list[3].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[3].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[3].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[3].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[3].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[3].getVertex(rdm[i]).getURL())
    else:
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[1], major_node_list[2]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                info[i].append(graph_list[idx].getVertex(rdm[i]).getId())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[idx].getVertex(rdm[i]).getURL())
        elif discount == "B":
            rdm = [major_node_list[1], list(graph_list[1].getVertex(major_node_list[1]).getConnections())[5].getId(), list(graph_list[1].getVertex(major_node_list[1]).getConnections())[10].getId()]
            for i in range(len(rdm)):
                info[i].append(graph_list[1].getVertex(rdm[i]).getId())
                info[i].append(graph_list[1].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[1].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[1].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[1].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[1].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[1].getVertex(rdm[i]).getURL())
        else:
            rdm = [major_node_list[0], list(graph_list[0].getVertex(major_node_list[0]).getConnections())[5].getId(), list(graph_list[0].getVertex(major_node_list[0]).getConnections())[10].getId()]
            for i in range(len(rdm)):
                info[i].append(graph_list[0].getVertex(rdm[i]).getId())
                info[i].append(graph_list[0].getVertex(rdm[i]).getImage())
                info[i].append(graph_list[0].getVertex(rdm[i]).getReview())
                info[i].append(graph_list[0].getVertex(rdm[i]).getDiscount())
                info[i].append(graph_list[0].getVertex(rdm[i]).getOriginal())
                info[i].append(graph_list[0].getVertex(rdm[i]).getCurrent())
                info[i].append(graph_list[0].getVertex(rdm[i]).getURL())
    return render_template('game_rec.html', info=info)

@app.route('/games_details/more', methods=['GET'])
def load_more():
    """Flask page that shows more game infos if user required to
    ------------------
    Return
    redered Flask page using template "more.html"
    """
    headers = {"user-agent": "Mozilla/5.0"}
    steam_dict = fetch_steam_data(headers)
    epic_dict = fetch_epic_data(headers)
    graph_list = []
    major_node_list = []
    graph_list, major_node_list= load_graph(steam_dict)
    # review = request.form['reviews']
    # discount = request.form['discount']
    global review
    global discount

    info = []
    for i in range(3):
        info.append([])
    if review == "m":
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[4], major_node_list[8]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
        elif discount == "B":
            rdm = [major_node_list[1], major_node_list[4], major_node_list[6]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
        else:
            rdm = [major_node_list[0], major_node_list[3], major_node_list[6]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
    elif review == 'v':
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[1], major_node_list[3]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
        elif discount == "B":
            rdm = [major_node_list[1], major_node_list[3], major_node_list[4]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
        else:
            for i in range(30):
                nbr_id = list(graph_list[3].getVertex(major_node_list[3]).getConnections())[i].getId()
                nbr_url = list(graph_list[3].getVertex(major_node_list[3]).getConnections())[i].getURL()
                info[i//10].append(nbr_id)
                info[i//10].append(nbr_url)
    else:
        if discount == "C":
            rdm = [major_node_list[0], major_node_list[1], major_node_list[2]]
            for i in range(len(rdm)):
                idx = major_node_list.index(rdm[i])
                for j in range(10):
                    nbr_id = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getId()
                    nbr_url = list(graph_list[idx].getVertex(major_node_list[idx]).getConnections())[j+1].getURL()
                    info[i].append(nbr_id)
                    info[i].append(nbr_url)
        elif discount == "B":
            for i in range(30):
                nbr_id = list(graph_list[1].getVertex(major_node_list[1]).getConnections())[i].getId()
                nbr_url = list(graph_list[1].getVertex(major_node_list[1]).getConnections())[i].getURL()
                info[i//10].append(nbr_id)
                info[i//10].append(nbr_url)
        else:
            for i in range(30):
                nbr_id = list(graph_list[0].getVertex(major_node_list[0]).getConnections())[i].getId()
                nbr_url = list(graph_list[0].getVertex(major_node_list[0]).getConnections())[i].getURL()
                info[i//10].append(nbr_id)
                info[i//10].append(nbr_url)
    return render_template('more.html', info=info)

@app.route('/epic_weekly_free_games', methods=['POST'])
def epic():
    """Flask page that shows weekly free games info retrieved from Epic platform
    ------------------
    Return
    redered Flask page using template "epic.html"
    """
    headers = {"user-agent": "Mozilla/5.0"}
    epic_dict = fetch_epic_data(headers)
    info = []
    _list = epic_dict['elements']
    for i in _list:
        id = i['title']
        des = i['description']
        image = i['keyImages'][0]['url']
        info.append([id, des, image])
    return render_template('epic.html', info=info)

@app.route('/search_games', methods=['POST'])
def search():
    """Flask page that shows top 3 search results based on user's input term.
    ------------------
    Return
    redered Flask page using template "search.html" if there are valid results,
    redered Flask page using template "exception.html" if not.
    """
    info = []
    term = request.form['term']
    headers = {"user-agent": "Mozilla/5.0"}
    _list = search_game(headers, term)
    if _list:
        for i in _list:
            info.append([i['title'], i['image'], i['review_sum'], i['discount'], i['original Price'], i['current Price'], i['url']])
        return render_template('search.html', info=info)
    else:
        return render_template('exception.html')

def save_graph():
    """writing graphs into a json file
    ------------------
    Parameters
    None
    ------------------
    Return
    None
    """
    headers = {"user-agent": "Mozilla/5.0"}
    _dict = fetch_steam_data(headers)
    graph_list, major_node_list = load_graph(_dict)
    dict = {}
    for i in range(10):
        # dict[f'graph {i}'] = {'major node': major_node_list[i], 'nodes': [list(graph_list[i].getVertex(major_node_list[i]) \
        #                                     .getConnections())[j].getId() for j in range(graph_list[i].getnum())]}
        dict[f'graph {i}'] = {'major node': major_node_list[i], 'nodes': list(graph_list[i].getVertices())}

    dumped_json_cache = json.dumps(dict)
    fw = open('graph.json',"w")
    fw.write(dumped_json_cache)
    fw.close()

if __name__ == "__main__":
    # app.run(debug=True, port=5000)
    save_graph()
