import praw
import config
from bs4 import BeautifulSoup
import requests
import os
import time
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:30.0) " +
                  "Gecko/20100101 Firefox/30.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

#bot_login grabs necessary information from config.py, and uses it to create a new reddit instance, named r, used to access reddit information tree.


def bot_login():
    r = praw.Reddit(username=config.username,
                    password=config.password,
                    client_id=config.client_id,
                    client_secret=config.client_secret,
                    user_agent="LyricFinderBot v0.2")

    print("Logged in...")
    return r

#get_puppies requires no arguments and retrieves most recent submission URL from the puppies subreddit,
#to maximize puppy randomness in thorough apology commentations. The function returns the url for commenting.


def get_puppies(r):
    puppies = r.subreddit('puppies').new(limit=1)

    for pup in puppies:
        puppy_url=pup.url

    return puppy_url

#reply_to_music takes r, the reddit instance, and the submissions_replied_to file. It obtains most recent music submissions
#then checks if they have been previously replied to and if they have not, calls the search_lyrics function, checks if lyrics
#were found, then comments on the original post accordingly.


def reply_to_music(r, submissions_replied_to):
    title = ""
    #get submissions from specified subreddits
    submissions = r.subreddit('PostHardcore+Metalcore+progmetal+Hardcore+melodichardcore+postmetal+progrockmusic+test').new(limit=10)
    print("Obtaining submissions...")

    #check each retrieved submission for validity

    for submission in submissions:
        if "you" in submission.url:
            print("Valid submission found!")
            title=submission.title

            # optimizing title for searching by replacing characters and ignoring phrases
            # in brackets or parentheses, as well as removing excess whitespace for
            #comment-friendly title
            title = re.sub('([\(\[]).*?([\)\]])', '', title)
            title = title.strip()
            title_to_post = title
            title = title.replace(" ", "+")
            print("Submission "+title+" being processed...")
            lyrics_to_comment = search_lyrics(title)

            #in the case that lyrics are not found, find a puppy to help console any comment readers, and print an apology
            if lyrics_to_comment == "Sorry, I wasn't able to find the lyrics for that song :(":
                puppy_to_post = get_puppies(r)
                submission.reply(lyrics_to_comment + "\n\n" + "Please accept [this]("+puppy_to_post+") picture of a puppy as an apology.")
                print("Apology printed ;(")
                submissions_replied_to.append(submission.id)

                #add replied-to submission to file so it is not analyzed again in a future search

                with open ("submissions_replied_to.txt", "a") as f:
                    f.write(submission.id)
                    f.write("\n")

                print("Sleeping for ten minutes until able to comment again...")
                time.sleep(600)

            #as long as lyrics were found, respond with said lyrics and acknowledge politeness
            else:
                submission.reply("Hi! I'm a bot that went to fetch the lyrics to this wonderful song; polite, aren't I?\n\n" +
                                 "Here are the lyrics to " + title_to_post + ":\n\n" +
                                 lyrics_to_comment
                                )

                print("Replied to submission" + submission.id)

                #add replied to submission to previously replied to submissions
                submissions_replied_to.append(submission.id)

                with open ("submissions_replied_to.txt", "a") as f:
                    f.write(submission.id)
                    f.write("\n")

                print("Sleeping for ten minutes until able to comment again...")
                time.sleep(600)

        else:
            print("No valid submissions found...")

#get_saved_submissions returns file to be written to when submissions which are not commented on are found
def get_saved_submissions():
    if not os.path.isfile("submissions_replied_to.txt"):
        submissions_replied_to = []

    else:
        with open("submissions_replied_to.txt", "r") as f:
            submissions_replied_to = f.read()
            submissions_replied_to = submissions_replied_to.split("\n")
            submissions_replied_to = list(filter(None, submissions_replied_to))

    return submissions_replied_to

#search_lyrics creates a search query on azlyrics.com, uses BeautifulSoup to parse through the results and the find
#the appropriate td item. If there is a td item, search results were found and lyrics can be retrieved. If not, return
#to reply_to_music with apology.


def search_lyrics(title):
    query = title

    #create search query url
    search_url = 'http://search.azlyrics.com/search.php?q='
    comp_url = search_url + query
    results = requests.get(comp_url)

    #format results
    search_soup = BeautifulSoup(results.text, "lxml")

    #find table data of appropriate class if it exists
    answer = search_soup.find('td', {'class': 'text-left visitedlyr'})

    if answer:
        #retrieve link in table data to redirect to new page where full lyrics are found
        link = answer.find('a')
        lyrics_url = link.get('href')

        #headers at top of main_bot.py are used to verify information and continue allowing access to azlyrics
        lyrics_results = requests.get(lyrics_url, headers=HEADERS)

        lyric_soup = BeautifulSoup(lyrics_results.text, "lxml")

        lyrics_content = ""
        #get div containing lyrics and copy lyrics to variable
        for div in lyric_soup.find_all('div', {'class': 'col-xs-12 col-lg-8 text-center'}):
            lyrics_content = div.find('div' , {'class': None}).get_text(separator='\n')

        return lyrics_content

    else:
        return "Sorry, I wasn't able to find the lyrics for that song :("


#main process in LyricFinderBot
r = bot_login()

def __main__():
    submissions_replied_to = get_saved_submissions()
    reply_to_music(r, submissions_replied_to)

#Leeeeeet's bump it
while (1):
    __main__()