# GreenPassVerifyBot
A telegram bot to verify the DGC/DCC QR Code
Try it at https://t.me/GPVerifyBot

## Quick Start

1. Create your own Telegram bot from @BotFather and take the bot token
2. Set in your environment the BOT_TOKEN variable\
   `export BOT_TOKEN="TOKEN"`
   
## Installation with virtualenv
1. Install virtualenv and setuptools package\
   `$ python3 -m pip install --upgrade pip`\
   `$ pip3 install virtualenv setuptools`
2. Make a note of the full file path to the custom version of Python you just installed\
   `$ which python3`
3. Create the virtual environment while you specify the version of Python you wish to use\
   `$ virtualenv -p /usr/bin/python3 venv`
4. Activate the new virtual environment\
   `$ source venv/bin/activate`
5. Install the requirement packages\
   `(venv) $ pip3 install -r requirements.txt`
6. Run the bot\
   `(venv) $ python3 bot.py`
