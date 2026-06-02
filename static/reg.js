(() => {
    const regForm = document.getElementById('username');
    const regBtn = document.getElementById('submitBtn');

    async function registerUser(e) {
    e.preventDefault();

    const res = await fetch('/set_username', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: regForm.value.trim()
        })
    });

    if (res.ok) {
        window.location.href = '/register';
    } else {
        alert('Registration failed');
    }
}

    regBtn.addEventListener('click', registerUser);
})();