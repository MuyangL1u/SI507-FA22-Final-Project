# SI507-FA22-Final-Project
This is my final project codes for SI507

## Required Python Packages
json

requests

flask

lxml

## Instruction to run the code
Directly run final.py with python3 environment installed. Next, type http://127.0.0.1:5000/ in any browser to visit the flask pages.

## User interaction instructions
There are three major kinds of user interactions:

1. Users can choose to receive some recommendations based on their preferences in terms of review grades and discounts. Those filter conditions are made into drop-down boxes for users to select. Each selection contains three options. After receiving preferences, users will be provided with the information of three games selected from the database in the second page. A third page, which is linked by a button on the second page, is available for users to view more results if they are not satisfied with the first three recommendations.
 
2. Users can type the name of the game or any terms in an input field to see the details of a specific game. Top 3 search results will be displayed. If there’s no matched results, users will be asked to go back to the default page to run again. 
    
3. Users can check out weekly free games offered on Epic platform. Games information will be provided along with the link to the official Epic website to claim all these games.

## Data structure
Data are grouped into 10 undirected graphs. Data is categorized based on the discounts and the review ratings. I’ve set three levels of discount: high(67% - 99%), medium(34% - 66%), low(0% - 33%) and three levels of approval ratings: overwhelmingly positive, very positive and mostly positive. In this case, there are 9 categories for the data to be separated. Games that have no review records so I grouped them into another category that I named “nomad”. I formed each category into a graph where each node represents a game so there’s 10 graphs in total. 
In each graph, there is a major node which represents the first game that falls into that category, and it directly connects every game of its kind. The weights don’t make any sense here so I set them all as 1. All nodes can be visited easily from the major node.
Graphs are stored in *graph.json*.

## Demo link
[click here](https://youtu.be/T4lY6QAs8RA)
