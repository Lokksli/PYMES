(() => {
  const wordInput = document.getElementById('wordInput');
  const isRegex = document.getElementById('isRegex');
  const addBtn = document.getElementById('addWord');
  const wordsList = document.getElementById('wordsList');

  async function fetchWords() {
    const res = await fetch('/admin/badwords');
    if (!res.ok) return;
    const words = await res.json();
    render(words);
  }

  function render(words) {
    wordsList.innerHTML = '';
    for (const w of words) {
      const div = document.createElement('div');
      div.className = 'word';
      div.textContent = `${w.word} ${w.is_regex ? '(regex)' : ''}`;
      const del = document.createElement('button');
      del.textContent = 'Delete';
      del.addEventListener('click', async () => {
        const r = await fetch('/admin/badwords/' + w.id, { method: 'DELETE' });
        if (r.ok) fetchWords();
      });
      div.appendChild(del);
      wordsList.appendChild(div);
    }
  }

  addBtn.addEventListener('click', async () => {
    const word = wordInput.value.trim();
    if (!word) return alert('word required');
    const res = await fetch('/admin/badwords', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ word, is_regex: isRegex.checked })
    });
    if (res.ok) {
      wordInput.value = '';
      isRegex.checked = false;
      fetchWords();
    } else {
      const e = await res.json();
      alert(e.error || 'failed');
    }
  });

  fetchWords();
})();
