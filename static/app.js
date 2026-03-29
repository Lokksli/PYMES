// client: fetches messages and users and updates the UI
(() => {
  const messagesEl = document.getElementById('messages');
  const sendBtn = document.getElementById('send');
  const messageInput = document.getElementById('messageInput');
  const usernameInput = document.getElementById('usernameInput');
  const setUsernameBtn = document.getElementById('setUsername');
  const currentUsername = document.getElementById('currentUsername');

  // set username in session and update UI
  async function setUsername() {
    const username = usernameInput.value.trim();
    if (!username) return;
    // send username to server to save in session and DB
    const res = await fetch('/set_username', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({username})
    });
    // update username 
    if (res.ok) {
      const data = await res.json();
      currentUsername.textContent = data.username;
      usernameInput.value = '';
    } else {
      alert('Failed to set username');
    }
  }

  // send a message to the server
  async function sendMessage() {
    const text = messageInput.value.trim();
    if (!text) return;
    const res = await fetch('/send_message', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    // clear input and refresh messages 
    if (res.ok) {
      messageInput.value = '';
      await fetchMessages();
    } else {
      const e = await res.json();
      alert(e.error || 'send failed');
    }
  }

  let lastMessages = [];

  // render message list into the messages pane
  function renderMessages(msgs) {
    messagesEl.innerHTML = '';
    for (const m of msgs) {
      const div = document.createElement('div');
      div.className = 'msg';
      const meta = document.createElement('div');
      meta.className = 'meta';
      meta.textContent = `${m.username} • ${m.created_at}`;
      const body = document.createElement('div');
      body.textContent = m.message;
      div.appendChild(meta);
      div.appendChild(body);
      messagesEl.appendChild(div);
    }
    messagesEl.scrollTop = messagesEl.scrollHeight;
  }

  // fetch messages from server periodically
  async function fetchMessages() {
    try {
      const res = await fetch('/messages');
      if (!res.ok) return;
      const msgs = await res.json();
      if (JSON.stringify(msgs) !== JSON.stringify(lastMessages)) {
        lastMessages = msgs;
        renderMessages(msgs);
      }
    } catch (err) {
      console.error('fetchMessages', err);
    }
  }

  // Users list rendering and polling
  let lastUsers = [];

  // render the users list in the sidebar
  function renderUsers(users) {
    const ul = document.getElementById('usersList');
    if (!ul) return;
    ul.innerHTML = '';
    for (const u of users) {
      const d = document.createElement('div');
      d.className = 'user';
      d.textContent = u.name;
      ul.appendChild(d);
    }
  }

  // fetch users from server periodically
  async function fetchUsers() {
    try {
      const res = await fetch('/users');
      if (!res.ok) return;
      const users = await res.json();
      if (JSON.stringify(users) !== JSON.stringify(lastUsers)) {
        lastUsers = users;
        renderUsers(users);
      }
    } catch (err) {
      console.error('fetchUsers', err);
    }
  }

  sendBtn.addEventListener('click', sendMessage);
  setUsernameBtn.addEventListener('click', setUsername);
  messageInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') sendMessage(); });
  usernameInput.addEventListener('keydown', (e) => { if (e.key === 'Enter') setUsername(); });

  // poll for messages
  fetchMessages();
  setInterval(fetchMessages, 1500);
    // poll for users a bit slower
    fetchUsers();
    setInterval(fetchUsers, 3000);

})();
