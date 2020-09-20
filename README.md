### Product Alert
So, I want to get that Playstation 5 but can't see any other way I can continuously monitor bunch of websites all the time. This simple script can be run with lambda function and will do the job.

![alert](https://media.giphy.com/media/huJmPXfeir5JlpPAx0/giphy.gif)

- Change the `config.ini` file to modify the email configuration.
- Change the `products_urls.json` file to modify websites data.
- Run: 
    - `python local_alert.py` to start the script on local computer.
    - `python lambda_alert.py` ~~start the script on lambda instance.~~ _(Not ready yet!)_
