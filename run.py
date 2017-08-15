#!/usr/bin/python3
from app import app


if __name__ == '__main__':
    context = ('mycert.pem', 'private.key')
    app.run(host='0.0.0.0', port=5353, debug=True, ssl_context=context)
