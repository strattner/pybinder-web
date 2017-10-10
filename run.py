#!/usr/bin/python3
import logging
from app import app


if __name__ == '__main__':
    # replace these with the name and location of your SSL certificate and private key
    context = ('mycert.pem', 'private.key')
    if 'LOGFILE' in app.config:
        handler = logging.FileHandler(app.config['LOGFILE'])
        handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter(fmt='%(asctime)s : %(message)s'))
        app.logger.addHandler(handler)
    app.run(host='0.0.0.0', port=5353, debug=True, ssl_context=context)
