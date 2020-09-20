import time
import json
import logging
import smtplib
import requests
import configparser
import concurrent.futures
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger('local_product_alert')
logger.setLevel(logging.DEBUG)
console = logging.StreamHandler()
logger.addHandler(console)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s: %(message)s')
console.setFormatter(formatter)

class ProductAlert:

    def __init__(self, config):
        self.smtp_host = config['email']['smtp_host']
        self.smtp_port = int(config['email']['smtp_port'])
        self.sender_email_id = config['email']['sender_email_id']
        self.sender_email_pass = config['email']['sender_email_pass']
        self.receiver_email_id = config['email']['receiver_email_id']
        self.agent = config['web']['agent']
        self.sleep_for = int(config['local']['sleep_for'])

    def send_email(self, website: str, product_url: str):
        """
        Send an email alert.
        :param website: website name
        :param product_url: product url
        :return: send email
        """
        subject = f"ALERT: {website} || PRODUCT AVAILABLE!!!"
        body = f"""
                <html>
                    <body align="center">
                        <br>
                        <br>
                        <p>
                            <img src="https://media.giphy.com/media/huJmPXfeir5JlpPAx0/giphy.gif" alt="ALERT" width="100%">
                            <h3>Please check the website</h3>
                            <br>
                            <h4>{product_url}</h4>
                        </p>
                    </body>
                </html>
                """
        message = MIMEMultipart()
        message["From"] = self.sender_email_id
        message["To"] = self.receiver_email_id
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))
        logger.debug('Email message created')
        text = message.as_string()
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email_id, self.sender_email_pass)
            server.sendmail(self.sender_email_id, self.receiver_email_id, text)

    def check_product_local(self, product_object: dict):
        """
        Check for product on webpage and send email alert.
        :param product_object: single product information dictionary from `product_urls.json`
        :return: either send email or sleep for few seconds and repeat the process
        """
        website = product_object['website']
        product_url = product_object['url']
        product_available = False
        while not product_available:
            response = requests.get(product_url, headers={'User-Agent': self.agent})
            soup = BeautifulSoup(response.text, "lxml")
            look_for_flag = False
            for look_for_str in product_object['look_for']:
                if not str(soup).lower().find(look_for_str.lower()) == -1:
                    look_for_flag = True
            if look_for_flag:
                logger.info(f'Hurray! Product available at: {website}')
                self.send_email(website, product_url)
                product_available = True
            else:
                time.sleep(self.sleep_for)
                logger.info(f'Product not available at: {website}, waiting: {self.sleep_for} seconds')

def main():
    config = configparser.ConfigParser()
    _ = config.read('config.ini')
    pa = ProductAlert(config)

    with open('product_urls.json', 'r') as f:
        product_urls = json.load(f)

    with concurrent.futures.ProcessPoolExecutor(max_workers=len(product_urls)) as executor:
        data = {
            executor.submit(
                pa.check_product_local,
                product_object
            ): product_object for product_object in product_urls
        }
        for future in concurrent.futures.as_completed(data):
            product_object = data[future]
            try:
                future.result()
            except Exception as exc:
                logging.error('generated an exception: {} at {}'.format(exc, product_object['website']))

if __name__ == '__main__':
    main()
