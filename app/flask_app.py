
# A very simple Flask Hello World app for you to get started with...

import hashlib
from functools import lru_cache
from collections import namedtuple
import json

from flask import Flask, jsonify

app = Flask(__name__)

User = namedtuple('User', 'name avatar token_hash')
class USERS:
    chase = User(name='Chase', avatar='', token_hash='3a7d3eb3a3b9c7655b936231b2e0b4af')
    rory = User(name='Rory', avatar='', token_hash='not yet set')

USER_TOKEN_HASHES = {
    USERS.chase.token_hash: USERS.chase,
}

UPDATES = {token_hash: False for token_hash in USER_TOKEN_HASHES}

LOG = open('log.txt', 'a')
POSTS = [  # should actually come from log
    {'user': 'Chase', 'message': 'how u?', 'avatar': ''}, 
    {'user': 'Rory', 'message': 'aight', 'avatar': ''},
]
LAST_RENDERED = json.dumps(dict(messages=POSTS))


JASONETTE_TEMPLATE = """
{
  "$jason":{
    "head":{
      "title":"Rory 'n' Chase",
      "actions":{
        "$foreground":{
          "trigger":"reload"
        },
        "$load":{
          "trigger":"reload"
        },
        "reload":{
          "type":"$network.request",
          "options":{
            "url":"http://rorynchase.pythonanywhere.com/messages/<TOKEN>",
            "method":"get"
          },
          "success":{
            "type":"$render"
          }
        },
        "say":{
          "type":"$network.request",
          "options":{
            "method":"post",
            "url":"http://rorynchase.pythonanywhere.com/messages/<TOKEN>",
            "data":{
              "text":"{{$get.message}}"
            }
          },
          "success":{
            "type":"$render"
          }
        }
      },
      "templates":{
        "body":{
          "style":{
            "border":"none",
            "align":"bottom"
          },
          "sections":[
            {
              "items":{
                "{{#each $jason.messages}}":{
                  "type":"horizontal",
                  "style":{
                    "spacing":"10"
                  },
                  "components":[
                    {
                      "type":"image",
                      "url":"{{avatar}}",
                      "style":{
                        "width":"30",
                        "height":"30",
                        "corner_radius":"15"
                      }
                    },
                    {
                      "type":"label",
                      "style":{
                        "font":"Courier",
                        "size":"14",
                        "color":"grey"
                      },
                      "text":"{{user}}: "
                    },
                    {
                      "type":"label",
                      "style":{
                        "font":"Courier",
                        "size":"14"
                      },
                      "text":"{{message}}"
                    }
                  ]
                }
              }
            }
          ],
          "footer":{
            "input":{
              "name":"message",
              "right":{
                "action":{
                  "trigger":"say"
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

INVALID_TOKEN_RESPONSE = json.dumps({'messages': [{'user': 'Error', 'message': 'Invalid user token!', 'avatar': ''}]})


#@lru_cache(max_size=32)
def hash_token(token):
    return hashlib.md5(token).hexdigest()


@app.route('/user/<string:token>', methods=['GET'])
def main(token):
    """Renders main jasonette view."""
    token_hash = hash_token(token)
    if token_hash not in USER_TOKEN_HASHES:
        return INVALID_TOKEN_RESPONSE, 403
    
    # return jasonette template rendered with provided token
    return JASONETTE_TEMPLATE.replace('<TOKEN>', token), 200


@app.route('/messages/<string:token>', methods=['GET', 'POST'])
def messages(token):
    """Allows post of message, returning all current messages."""
    token_hash = hash_token(token)
    
    # if post, do post, write to log
    # if post, needs update
    
    # if not post:
    needs_update = UPDATES.get(token_hash)
    if needs_update is None:
        return INVALID_TOKEN_RESPONSE, 403
    
    if not needs_update:
        return LAST_RENDERED, 200
    
    # render
    # cache render
    
    UPDATES[token_hash] = False
    
    return LAST_RENDERED, 200
