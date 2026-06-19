from flask import Flask, request, render_template, jsonify, session
import os
import messages_db as mdb
import users_db as udb
import moderator as mod
import bans_db as bans_db

class User:
    # user class with id and name
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name

    def __repr__(self):
        return f"User(id={self.id!r}, name={self.name!r})"


class MessengerApp:
    def __init__(self, import_name=__name__):
        self.app = Flask(import_name, template_folder="templates", static_folder="static")
        self.app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret-change-me')
        # try to create DBs 
        try:
            mdb.init_db()
            udb.init_db()
            bans_db.init_db()
            mod.init()
        except Exception:
            pass

        self.register_routes()
       
    def register_routes(self):
        app = self.app

        @app.route('/')
        def index():
            # render main UI and show username
            return render_template('register.html')

        @app.route('/set_username', methods=['POST'])
        def set_username():
            # set username in session and add to users DB
            data = request.get_json(force=True, silent=True) or {}
            # delete whitespace and validate username
            username = (data.get('username') or '').strip()
            if not username:
                return jsonify({'error': 'username required'}), 400
            session['username'] = username

            try:
                udb.add_user(username)
            except Exception:
                pass
            
            return jsonify({'ok': True, 'username': username})
        

        @app.route('/send_message', methods=['POST'])
        def send_message():
            # accept a message and store it
            data = request.get_json(force=True, silent=True) or {}
            random_username = f"guest{os.urandom(4).hex()}"
            if 'username' not in session and 'username' not in data:
                session['username'] = random_username
            username = session.get('username') or data.get('username') or random_username
            message = (data.get('message') or '').strip()
            if not message:
                return jsonify({'error': 'empty message'}), 400

            # run moderator check before storing
            try:
                res = mod.check_and_handle_message(username, message)
            except Exception:
                res = {'action': 'ok'}

            if res.get('action') == 'user_banned':
                return jsonify({'error': 'user banned', 'seconds_left': res.get('seconds_left')}), 403
            if res.get('action') == 'banned':
                # don't store the offending message
                return jsonify({'error': 'message contained banned word', 'ban_seconds': res.get('ban_seconds')}), 403

            # store message when moderator OK
            mdb.add_message(username, message)
            return jsonify({'ok': True})

        @app.route('/messages', methods=['GET'])
        def messages():
            # return recent messages as JSON
            msgs = mdb.get_recent_messages(limit=200)
            return jsonify(msgs)

        @app.route('/users', methods=['GET'])
        def users():
            # return known users as JSON
            try:
                users = udb.get_users()
            except Exception:
                users = []
            return jsonify(users)

        # admin UI for managing badwords
        @app.route('/admin', methods=['GET'])
        def admin_ui():
            return render_template('admin.html')

        @app.route('/admin/badwords', methods=['GET'])
        def admin_list_badwords():
            try:
                import badwords_db as bdb
                bdb.init_db()
                words = bdb.get_all_words()
            except Exception:
                words = []
            return jsonify(words)

        @app.route('/admin/badwords', methods=['POST'])
        def admin_add_badword():
            data = request.get_json(force=True, silent=True) or {}
            word = (data.get('word') or '').strip()
            is_regex = bool(data.get('is_regex'))
            if not word:
                return jsonify({'error': 'word required'}), 400
            import badwords_db as bdb
            bdb.init_db()
            try:
                bdb.add_word(word, is_regex=is_regex)
            except Exception:
                return jsonify({'error': 'failed to add word'}), 500
            return jsonify({'ok': True})

        @app.route('/admin/badwords/<int:id>', methods=['DELETE'])
        def admin_delete_badword(id):
            import badwords_db as bdb
            try:
                bdb.delete_word(id)
            except Exception:
                return jsonify({'error': 'delete failed'}), 500
            return jsonify({'ok': True})

        @app.route('/admin/bans', methods=['GET'])
        def admin_list_bans():
            # return list of current bans (username + seconds_left)
            try:
                conn = bans_db.get_conn()
                c = conn.cursor()
                c.execute('SELECT username, banned_until FROM bans')
                rows = c.fetchall()
                conn.close()
                import time
                now = int(time.time())
                out = []
                for u, until in rows:
                    seconds_left = max(0, int(until) - now)
                    out.append({'username': u, 'seconds_left': seconds_left, 'banned_until': until})
            except Exception:
                out = []
            return jsonify(out)
        
        # deleting all messages (only for testin purpose)
        @app.route('/delete_messages', methods=['POST'])
        def delete_messages():
            # delete all messages (for testing)
            mdb.delete_all_messages()
            return jsonify({'ok': True})
        
        #deleting a message by id for moderation
        @app.route('/delete_message', methods=['POST'])
        def delete_message_by_id():
            data = request.get_json(force=True, silent=True) or {}
            id = data.get('id')
            if not id:
                return jsonify({'error': 'message id required'}), 400
            mdb.delete_message(id)
            return jsonify({'ok': True})
        
        @app.route('/register', methods=['GET'])
        def register():
            # render registration page
            username = session.get('username')
            return render_template('index.html', username=username)


def create_app():
    # factory that returns the Flask app instance
    return MessengerApp().app

if __name__ == '__main__':
    # run development server when executed directly
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


