import praw
import config
from bs4 import BeautifulSoup
import requests
import os
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:30.0) " +
                  "Gecko/20100101 Firefox/30.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}


def bot_login():
    r = praw.Reddit(username = config.username,
                    password = config.password,
                    client_id = config.client_id,
                    client_secret = config.client_secret,
                    user_agent = "LyricFinderBot v0.1")

    print("Logged in...")
    return r


def reply_to_music(r, submissions_replied_to):
    title = ""
    submissions = r.subreddit('test').hot(limit=10)

    print("Obtaining submissions...")

    for submission in submissions:
        if "you" in submission.url and submission.id not in submissions_replied_to:
            print("Valid submission found!")
            title = submission.title

            lyrics_to_comment = search_lyrics(title)

            if lyrics_to_comment == "Sorry, I wasn't able to find the lyrics for that song :(":
                print("Apology printed ;(")
                submission.reply(lyrics_to_comment + "\n\n" + "Please accept [this](http://i.imgur.com/f3B9WaZ.png) picture of a puppy as an apology.")
                submissions_replied_to.append(submission.id)

                with open ("submissions_replied_to.txt", "a") as f:
                    f.write(submission.id)
                    f.write("\n")

            else:
                submission.reply("Hi! I'm a bot to go and fetch the lyrics to this wonderful song; polite, aren't I?\n\n" +
                                 "Here are the lyrics to " + title + ":\n\n" +
                                 lyrics_to_comment
                                )

                print("Replied to submission" + submission.id)

                submissions_replied_to.append(submission.id)

                with open ("submissions_replied_to.txt", "a") as f:
                    f.write(submission.id)
                    f.write("\n")

        else:
            print("No valid submissions found...")

    print("Sleeping for 10 minutes...")
    time.sleep(600)


def get_saved_submissions():
    if not os.path.isfile("submissions_replied_to.txt"):
        submissions_replied_to = []

    else:
        with open("submissions_replied_to.txt", "r") as f:
            submissions_replied_to = f.read()
            submissions_replied_to = submissions_replied_to.split("\n")
            submissions_replied_to = list(filter(None, submissions_replied_to))

    return submissions_replied_to


def search_lyrics(title):
    query = title

    query = query.replace(" ", "+")
    search_url = 'http://search.azlyrics.com/search.php?q='
    comp_url = search_url + query
    results = requests.get(comp_url)

    search_soup = BeautifulSoup(results.text, "lxml")

    if search_soup.find_all('td', {'class': 'text-left visitedlyr'}) == None:
        for td in search_soup.find_all('td', {'class': 'text-left visitedlyr'}):
            link = td.find('a')
            lyrics_url = link.get('href')

        lyrics_results = requests.get(lyrics_url, headers=HEADERS)

        lyric_soup = BeautifulSoup(lyrics_results.text, "lxml")

        for div in lyric_soup.find_all('div', {'class': 'col-xs-12 col-lg-8 text-center'}):
            lyrics_content = div.find('div' , {'class': None}).text

        return lyrics_content

    else:
        return "Sorry, I wasn't able to find the lyrics for that song :("

r = bot_login()
submissions_replied_to = get_saved_submissions()
print(submissions_replied_to)

while True:
    reply_to_music(r, submissions_replied_to)
