#########################################
##### Name:  Muyang Liu             #####
##### Uniqname:   terryliu          #####
#########################################
import json
import requests
# from bs4 import BeautifulSoup
from lxml import etree

class Vertex:
    def __init__(self, key):
        self.id = key
        self.connectedTo = {}
        self.color = 'white'
        self.dist = 0
        self.pred = None
        self.review_grade = 'Unknown'
        self.discount_grade = 'Unknown'

    def addNeighbor(self, nbr, weight=0):
        self.connectedTo[nbr] = weight
    def setColor(self,color):
        self.color = color
    def setDistance(self,d):
        self.dist = d
    def setPred(self,p):
        self.pred = p
    def setGrade(self,x):
        self.review_grade = x
    def setDiscount(self,x):
        self.discount_grade = x

    def getDiscount(self):
        return self.discount_grade
    def getGrade(self):
        return self.review_grade
    def getPred(self):
        return self.pred
    def getDistance(self):
        return self.dist
    def getColor(self):
        return self.color
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
                if len(j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')) == 0:
                    continue
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
                game_discount = j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()')[0]
                # except:
                #     print(j.xpath('.//div[@class="col search_discount responsive_secondrow"]/span/text()'))
                game_original_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/span/strike/text()')[0]
                game_current_price = j.xpath('.//div[@class="col search_price discounted responsive_secondrow"]/text()')[1].strip()
                # temp.append({'title': game_title, 'discount': game_discount, 'original Price': game_original_price, 'current Price': game_current_price})
                temp.append({'title': game_title, 'url': game_url, 'image': game_image, 'release_date': game_release_date,\
                            'review_sum': game_review_sum, 'discount': game_discount, 'original Price': game_original_price, 'current Price': game_current_price})
                app_cnt += 1
            # print(temp)
            dict[key] = temp
        save_cache(dict, 'steam.json')
        # print(dict)
        return dict

def fetch_epic_data(headers):
    epic_dict = open_cache('epic_free_games.json')
    if epic_dict:
        return epic_dict
    else:
        epic_base_url = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?"
        data = {'locale': 'en-US', 'country': 'US', 'allowCountries': 'US'}
        response = requests.get(epic_base_url, headers=headers, params=data)
        a = json.loads(response.text)
        dicts = a['data']['Catalog']['searchStore']
        # print(dict)
        save_cache(dicts, 'epic_free_games.json')
        return dicts

def load_graph(dict):
    page_cnt = 0
    A1 = []
    A2 = []
    A3 = []
    B1 = []
    B2 = []
    B3 = []
    C1 = []
    C2 = []
    C3 = []
    nomad = []
    g1 = Graph()
    g2 = Graph()
    g3 = Graph()
    g4 = Graph()
    g5 = Graph()
    g6 = Graph()
    g7 = Graph()
    g8 = Graph()
    g9 = Graph()
    g_nomad = Graph()
    while page_cnt < 300:
        for i in dict[f'page {page_cnt}']:
            try:
                review_word = i['review_sum'][0].split(' ')[0]
                discount = int(i['discount'].replace('-', '').replace('%', ''))
                if review_word == 'Overwhelmingly':
                    if discount > 66:
                        A1.append(i['title'])
                    elif discount > 33:
                        A2.append(i['title'])
                    else:
                        A3.append(i['title'])
                elif review_word == 'Very':
                    if discount > 66:
                        B1.append(i['title'])
                    elif discount > 33:
                        B2.append(i['title'])
                    else:
                        B3.append(i['title'])
                else:
                    if discount > 66:
                        C1.append(i['title'])
                    elif discount > 33:
                        C2.append(i['title'])
                    else:
                        C3.append(i['title'])
            except:
                nomad.append(i['title'])

        page_cnt += 1

    for i in range(1, len(A1)):
        g1.addEdge(A1[0], A1[i], weight=1)
        g1.addEdge(A1[i], A1[0], weight=1)

    for i in range(1, len(A2)):
        g2.addEdge(A2[0], A2[i], weight=1)
        g2.addEdge(A2[i], A2[0], weight=1)

    for i in range(1, len(A3)):
        g3.addEdge(A3[0], A3[i], weight=1)
        g3.addEdge(A3[i], A3[0], weight=1)

    for i in range(1, len(B1)):
        g4.addEdge(B1[0], B1[i], weight=1)
        g4.addEdge(B1[i], B1[0], weight=1)

    for i in range(1, len(B2)):
        g5.addEdge(B2[0], B2[i], weight=1)
        g5.addEdge(B2[i], B2[0], weight=1)

    for i in range(1, len(B3)):
        g6.addEdge(B3[0], B3[i], weight=1)
        g6.addEdge(B3[i], B3[0], weight=1)

    for i in range(1, len(C1)):
        g7.addEdge(C1[0], C1[i], weight=1)
        g7.addEdge(C1[i], C1[0], weight=1)

    for i in range(1, len(C2)):
        g8.addEdge(C2[0], C2[i], weight=1)
        g8.addEdge(C2[i], C2[0], weight=1)

    for i in range(1, len(C3)):
        g9.addEdge(C3[0], C3[i], weight=1)
        g9.addEdge(C3[i], C3[0], weight=1)

    for i in range(1, len(nomad)):
        g_nomad.addEdge(nomad[0], nomad[i], weight=1)
        g_nomad.addEdge(nomad[i], nomad[0], weight=1)

    for node in g1.getVertices():
        vertex = g1.getVertex(node)
        vertex.setGrade('A')
        vertex.setDiscount('A')

    for node in g2.getVertices():
        vertex = g2.getVertex(node)
        vertex.setGrade('A')
        vertex.setDiscount('B')

    for node in g3.getVertices():
        vertex = g3.getVertex(node)
        vertex.setGrade('A')
        vertex.setDiscount('C')

    for node in g4.getVertices():
        vertex = g4.getVertex(node)
        vertex.setGrade('B')
        vertex.setDiscount('A')

    for node in g5.getVertices():
        vertex = g5.getVertex(node)
        vertex.setGrade('B')
        vertex.setDiscount('B')

    for node in g6.getVertices():
        vertex = g6.getVertex(node)
        vertex.setGrade('B')
        vertex.setDiscount('C')

    for node in g7.getVertices():
        vertex = g7.getVertex(node)
        vertex.setGrade('C')
        vertex.setDiscount('A')

    for node in g8.getVertices():
        vertex = g8.getVertex(node)
        vertex.setGrade('C')
        vertex.setDiscount('B')

    for node in g9.getVertices():
        vertex = g9.getVertex(node)
        vertex.setGrade('C')
        vertex.setDiscount('C')

    return g1, g2, g3, g4, g5, g6, g7, g8, g9, g_nomad

def main():
    headers = {"user-agent": "Mozilla/5.0"}
    steam_dict = fetch_steam_data(headers)
    epic_dict = fetch_epic_data(headers)

    g1, g2, g3, g4, g5, g6, g7, g8, g9, g_nomad = load_graph(steam_dict)
    '''test graph'''
    # print(g1.getVertex('killer7').__str__())
    # print(g_nomad.__contains__())

if __name__ == "__main__":
    main()
