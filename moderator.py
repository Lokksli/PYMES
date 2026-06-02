import messages_db as mdb
import users_db as udb
import badwords_db as bdb

messages = mdb.get_recent_messages()


import messages_db as mdb
import users_db as udb
import badwords_db as bdb

messages = mdb.get_recent_messages()

for i in messages:
    print(i['message'])
    id = 1
    while True:
        word = bdb.get_a_word_by_id(id)
        if word is None:    # no more words
            break
        word = word[0]      # extract string from tuple
        if word in i['message']:
            mdb.delete_message(i['id'])
            print("Message deleted")
            break
        id += 1