from dotenv import load_dotenv
from os import getenv, remove
from io import BytesIO
from PIL import Image
from tempfile import mkstemp
from datetime import datetime

import greenpass
import botogram
import html

load_dotenv()

bot = botogram.create(getenv('BOT_TOKEN'))
bot.about = "This telegram bot will decode and verify the DGC/DCC QR Code.\n" \
            "The bot will only check if the content is authentic, depending on your local rules " \
            "the certificate may not be accepted as a valid Green Pass.\n" \
            "This bot does not replace the official verifier app from your local health institution"

def format_time(ts):
    return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def decode(chat, content):
    cert, valid = greenpass.certinfo(content)

    if cert is not None:
        annotated = html.escape(greenpass.annotate(cert["certificate"]))
        emoji = "✅" if valid else "❌"

        text = f"Issuer: {cert['issuer']}\nGeneration date: {format_time(cert['generated_ad'])}\nExpiration date: {format_time(cert['expiry'])}\nVerified: {emoji}\nContent:\n<pre>{annotated}</pre>"
    else:
        text = "Could not decode certificate"

    chat.send(text)

@bot.command("decode")
def command_decode(chat, args):
    """Decode the base45 from the QR if scanned manually"""
    decode(chat, ' '.join(args).encode('utf-8'))

@bot.process_message
def process_message(chat, message):
    file_path = None
    if message.photo is not None:
        file_path = mkstemp()[1]
        message.photo.save(file_path)
    #elif message.document is not None:
        #file = download_file(message.document.file_id)

    if file_path is not None:
        img = Image.open(file_path)
        qr_content = greenpass.read_qr(img)
        remove(file_path)
        if qr_content is None:
            chat.send('No QR Code found')
            return

    decode(chat, qr_content)

bot.run()
