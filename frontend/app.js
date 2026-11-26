const API = '/api/v1/';
const AUTH = '/auth/'
const TYPE_NAMES = { clothes: 'Одежда', electronics: 'Электроника', other: 'Разное' };

// ── Токены ────────────────────────────────────────────────
const getAccess  = () => localStorage.getItem('access');
const getRefresh = () => localStorage.getItem('refresh');
const setTokens  = (a, r) => {
  localStorage.setItem('access', a);
  if (r) localStorage.setItem('refresh', r);
};
const clearTokens = () => {
  localStorage.removeItem('access');
  localStorage.removeItem('refresh');
};

// ── fetch с автообновлением access-токена ────────────────
async function apiFetch(path, opts = {}) {
  const headers = { 'Content-Type': 'application/json', ...(opts.headers || {}) };
  const token = getAccess();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  let res = await fetch(`${API}${path}`, { ...opts, headers });

  if (res.status === 401 && getRefresh()) {
    const ok = await tryRefresh();
    if (ok) {
      headers['Authorization'] = `Bearer ${getAccess()}`;
      res = await fetch(`${API}${path}`, { ...opts, headers });
    }
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`${res.status}: ${text}`);
  }
  return res.status === 204 ? null : res.json();
}

async function tryRefresh() {
  const res = await fetch(`${AUTH}jwt/refresh/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ refresh: getRefresh() }),
  });
  if (!res.ok) return false;
  const data = await res.json();
  setTokens(data.access);
  return true;
}

// ── Логин / логаут ────────────────────────────────────────
async function login(username, password) {
  const res = await fetch(`${AUTH}jwt/create/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Неверный логин или пароль');
  const data = await res.json();
  setTokens(data.access, data.refresh);
}

function logout() {
  clearTokens();
  renderAuthState();
}

// ── UI ────────────────────────────────────────────────────
function renderAuthState() {
  const authed = !!getAccess();
  document.getElementById('login-section').hidden = authed;
  document.getElementById('app-section').hidden = !authed;
  if (authed) loadParcels();
}

async function loadParcels() {
  try {
    const data = await apiFetch('parcels/');
    const items = data.results || data;
    const tbody = document.getElementById('parcels-body');
    tbody.innerHTML = items.map(p => `
      <tr>
        <td>${escapeHtml(p.name)}</td>
        <td>${p.weight}</td>
        <td>${p.cost}</td>
        <td>${TYPE_NAMES[p.parcel_type] || p.parcel_type}</td>
        <td>${p.delivery_cost}</td>
      </tr>
    `).join('') || '<tr><td colspan="5">Пока нет посылок</td></tr>';
  } catch (e) {
    console.error('loadParcels', e);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[c]));
}

// ── Слушатели ─────────────────────────────────────────────
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const err = document.getElementById('login-error');
  err.textContent = '';
  try {
    await login(
      document.getElementById('username').value,
      document.getElementById('password').value,
    );
    renderAuthState();
  } catch (ex) {
    err.textContent = ex.message;
  }
});

document.getElementById('logout-btn').addEventListener('click', logout);

document.getElementById('parcel-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const err = document.getElementById('parcel-error');
  err.textContent = '';
  try {
    await apiFetch('parcels/', {
      method: 'POST',
      body: JSON.stringify({
        name: document.getElementById('parcel-name').value,
        weight: document.getElementById('parcel-weight').value,
        cost: document.getElementById('parcel-cost').value,
        parcel_type: document.getElementById('parcel-type').value,
      }),
    });
    e.target.reset();
    loadParcels();
  } catch (ex) {
    err.textContent = ex.message;
  }
});

document.getElementById('chat-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const input = document.getElementById('chat-question');
  const log = document.getElementById('chat-log');
  const q = input.value.trim();
  if (!q) return;

  log.innerHTML += `<div class="msg user">${escapeHtml(q)}</div>`;
  input.value = '';

  const botMsg = document.createElement('div');
  botMsg.className = 'msg bot';
  botMsg.textContent = 'Думаю...';
  log.appendChild(botMsg);

  try {
    const res = await fetch('/support/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAccess()}`,
      },
      body: JSON.stringify({ question: q }),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(`${res.status}: ${text}`);
    }

    const data = await res.json();
    botMsg.textContent = data.answer;
  } catch (ex) {
    botMsg.textContent = `Ошибка: ${ex.message}`;
    botMsg.classList.add('error');
  }
  log.scrollTop = log.scrollHeight;
});

// ── Старт ─────────────────────────────────────────────────
renderAuthState();