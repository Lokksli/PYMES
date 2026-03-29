from flask import Flask, request, render_template, jsonify, session
import os
import messages_db as mdb
import users_db as udb


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
        except Exception:
            pass

        self.register_routes()

    def register_routes(self):
        app = self.app

        @app.route('/')
        def index():
            # render main UI and show username
            username = session.get('username')
            return render_template('index.html', username=username)

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


def create_app():
    # factory that returns the Flask app instance
    return MessengerApp().app


if __name__ == '__main__':
    # run development server when executed directly
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)


