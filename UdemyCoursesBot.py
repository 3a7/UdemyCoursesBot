import requests, re, logging, schedule, time, telebot, os, sys, threading
from bs4 import BeautifulSoup

# Websites will be used 
# https://www.couponseagle.com/
# https://onehack.us/
# https:///www.real.discount

# Telegram bot token
bot_token = '6360915118:AAEAFEFg6d7fvZjFjQocfprOzdiPJSewMD0'
bot = telebot.TeleBot(bot_token)

# Log format for all messages
logging.basicConfig(format='[%(asctime)s] - %(message)s',level=logging.INFO)

# Scrape courses class
class Program():
    def __init__(self):
        self.links = set()
        self.last_update = None
        self.scrape_course()

    # To scrape courses
    def scrape_course(self):
        self.temp_links = set()
        self.website1()
        self.website2()
        self.website3()
        logging.info(f'Scrabed total of {len(self.temp_links)} unique courses from all websites')
        self.links.clear()
        self.last_update = time.asctime()
        self.links = self.temp_links.copy()

    def website1(self):
        c = 0
        try:
            url = 'https://www.couponseagle.com/'
            header = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'}
            r = requests.get(url,headers=header,timeout=10)
            soup = BeautifulSoup(r.text,'html.parser')
            all_links = soup.find_all('h2',class_='font130 mt0 mb10 mobfont120 lineheight25')

            for course in all_links:
                try:
                    r = requests.get(course.find('a')['href'], headers=header).text
                    link = re.search(r'href="https://www.udemy.com/course/[^"]*',r)
                    self.temp_links.add(link.group()[6:])
                    c += 1
                except:
                    pass
        except Exception as exe:
            logging.error(f'Exception while scraping website1 {exe}')
        logging.info(f'From website1 {c} courses scraped')



    def website2(self):
        c = 0
        try:
            header = {
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
                }
            r = requests.get('https://onehack.us/',headers=header,timeout=10)
            soup = BeautifulSoup(r.text,'html.parser')
            elements = soup.find_all('a',class_='title raw-link raw-topic-link')

            for text in elements:
                if str(text.text).startswith('[COUPON]') or str(text.text).startswith('[COUPONS]'):
                    cop_link = requests.get(text['href'],headers=header).text
                    cop_links = re.findall(r'\"https://www.udemy.com/course/.*?couponCode=[A-z0-9]{,}\\"',cop_link)
                    for course in cop_links:
                        self.temp_links.add(course[1:-2])
                        c += 1
        except Exception as exe:
            logging.error(f'Exception while scraping website2 {exe}')
        logging.info(f'From website2 {c} courses scraped')

    def website3(self):
        c = 0
        try:
            url = 'https://www.real.discount/api-web/all-courses/?store=Udemy&page=1&per_page=10&orderby=undefined&free=0&search=&language=&cat='
            headers = {'Host': 'www.real.discount',
            'Sec-Ch-Ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Ch-Ua-Mobile': '?0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://www.real.discount/',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Priority': 'u=1, i',
            'Connection': 'close'
            }
            courses = requests.get(url,headers=headers,timeout=10).json()['results']
            for course in courses:
                self.temp_links.add(course['url'])
                c += 1
        except Exception as exe:
            logging.error(f'Exception while scraping website3 {exe}')
        logging.info(f'From website3 {c} courses scraped')

Main = Program()
greetings = r'''
This simple bot is made by @A7_acc, it gives you the latest Udemy courses that has 100% off on them

Simply send /send_courses to erceive the latest up-to-date 100% off udemy courses'''

# Users that used the bot in the last hour
last_hour_users = list()

# Handles all messages sent from users to the bot
@bot.message_handler(func=lambda message: True)
def telegram_handler(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, 'Welcome '+str(message.from_user.first_name)+'!!')
        bot.send_message(message.chat.id, greetings)
    elif message.text == '/send_courses':
        bot.reply_to(message, 'Sending the courses...')

        for course in Main.links:
            bot.send_message(message.chat.id, course)
        bot.send_message(message.chat.id,'Links last update: '+Main.last_update)
        
    elif message.text == '/about':
        bot.send_message(message.chat.id, greetings)

    else:
        bot.send_message(message.chat.id, 'Please send /send_courses or /about to continue')

    # Saving usernames to last_hour_users
    if message.from_user.username not in last_hour_users:
        last_hour_users.append(message.from_user.username)

# Infinite polling and error avoidance
def bot_polling():
    while True:
        try:
            bot.infinity_polling()
        except:
            os.execv(sys.argv[0], sys.argv)

# Seperate thread for the bot polling deamon
logging.critical('Starting bot...')
polling_thread = threading.Thread(target=bot_polling)
polling_thread.daemon = True
polling_thread.start()

def print_last_hour_users():
    logging.info(f'Users that used your bot in last hour are {len(last_hour_users)}:{last_hour_users}')
    last_hour_users.clear()

# Scraping the courses every hour using schedule
schedule.every().hour.do(Main.scrape_course)
schedule.every().hour.do(print_last_hour_users)

while True:
    schedule.run_pending()
    time.sleep(1)