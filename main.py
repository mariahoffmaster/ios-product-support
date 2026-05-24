<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Badger Support — Ticket Dashboard</title>
<style>
  :root {
    --bg: #f4f5f7;
    --white: #ffffff;
    --border: #e1e4e8;
    --text: #1a1a2e;
    --muted: #6b7280;
    --blue: #2563eb;
    --blue-light: #eff6ff;
    --green: #16a34a;
    --green-light: #f0fdf4;
    --yellow: #d97706;
    --yellow-light: #fffbeb;
    --purple: #7c3aed;
    --purple-light: #f5f3ff;
    --red: #dc2626;
    --red-light: #fef2f2;
    --gray: #6b7280;
    --gray-light: #f9fafb;
    --unlock-teal: #0891b2;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: var(--bg); color: var(--text); min-height: 100vh; }

  /* Header */
  .header { background: var(--white); border-bottom: 1px solid var(--border);
             padding: 16px 32px; display: flex; align-items: center;
             justify-content: space-between; }
  .header h1 { font-size: 20px; font-weight: 700; color: var(--unlock-teal); }
  .header .subtitle { font-size: 13px; color: var(--muted); margin-top: 2px; }
  .refresh-btn { background: var(--blue); color: white; border: none;
                 padding: 8px 16px; border-radius: 6px; cursor: pointer;
                 font-size: 13px; font-weight: 500; }
  .refresh-btn:hover { background: #1d4ed8; }

  /* API config */
  .api-bar { background: #fff8f0; border-bottom: 1px solid #fde68a;
             padding: 10px 32px; display: flex; align-items: center; gap: 12px; }
  .api-bar label { font-size: 13px; font-weight: 500; color: var(--yellow); }
  .api-bar input { border: 1px solid #fde68a; border-radius: 5px; padding: 5px 10px;
                   font-size: 13px; width: 420px; }
  .api-bar button { background: var(--yellow); color: white; border: none;
                    padding: 6px 14px; border-radius: 5px; cursor: pointer; font-size: 13px; }

  /* Summary cards */
  .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
             gap: 16px; padding: 24px 32px 0; }
  .card { background: var(--white); border: 1px solid var(--border); border-radius: 10px;
          padding: 16px 20px; }
  .card .num  { font-size: 32px; font-weight: 700; line-height: 1; }
  .card .lbl  { font-size: 12px; color: var(--muted); margin-top: 4px; font-weight: 500;
                text-transform: uppercase; letter-spacing: 0.04em; }
  .card.total .num { color: var(--text); }
  .card.new   .num { color: var(--blue); }
  .card.assigned .num { color: var(--purple); }
  .card.inprogress .num { color: var(--yellow); }
  .card.resolved .num { color: var(--green); }

  /* Category breakdown */
  .breakdown { padding: 20px 32px 0; display: grid;
               grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; }
  .cat-card { background: var(--white); border: 1px solid var(--border);
              border-radius: 8px; padding: 14px 18px;
              border-left: 4px solid var(--border); }
  .cat-card.badger       { border-left-color: var(--blue); }
  .cat-card.excel        { border-left-color: var(--purple); }
  .cat-card.dealdata     { border-left-color: var(--yellow); }
  .cat-card.adhoc        { border-left-color: var(--unlock-teal); }
  .cat-card .cat-name    { font-size: 12px; font-weight: 600; color: var(--muted);
                           text-transform: uppercase; letter-spacing: 0.04em; }
  .cat-card .cat-count   { font-size: 26px; font-weight: 700; margin-top: 2px; }
  .cat-card .cat-assignee { font-size: 12px; color: var(--muted); margin-top: 2px; }

  /* Filters */
  .filters { padding: 20px 32px 0; display: flex; gap: 12px; flex-wrap: wrap;
             align-items: center; }
  .filters label { font-size: 13px; font-weight: 500; color: var(--muted); }
  .filters select, .filters input {
    border: 1px solid var(--border); border-radius: 6px; padding: 6px 10px;
    font-size: 13px; background: var(--white); color: var(--text); }
  .filters select:focus, .filters input:focus { outline: 2px solid var(--blue); }
  .clear-btn { font-size: 13px; color: var(--blue); cursor: pointer;
               background: none; border: none; text-decoration: underline; }

  /* Table */
  .table-wrap { padding: 20px 32px 40px; overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; background: var(--white);
          border: 1px solid var(--border); border-radius: 10px; overflow: hidden; }
  thead th { background: var(--gray-light); padding: 10px 14px; text-align: left;
             font-size: 12px; font-weight: 600; color: var(--muted);
             text-transform: uppercase; letter-spacing: 0.04em;
             border-bottom: 1px solid var(--border); }
  tbody tr { border-bottom: 1px solid var(--border); }
  tbody tr:last-child { border-bottom: none; }
  tbody tr:hover { background: #f8fafc; }
  td { padding: 11px 14px; font-size: 13px; vertical-align: middle; }
  .ticket-id { font-weight: 700; color: var(--muted); white-space: nowrap; }
  .desc-cell { max-width: 320px; }
  .desc-text { overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2;
               -webkit-box-orient: vertical; line-height: 1.4; }

  /* Badges */
  .badge { display: inline-block; padding: 3px 8px; border-radius: 12px;
           font-size: 11px; font-weight: 600; white-space: nowrap; }
  .badge-badger    { background: var(--blue-light);   color: var(--blue); }
  .badge-excel     { background: var(--purple-light);  color: var(--purple); }
  .badge-dealdata  { background: var(--yellow-light);  color: var(--yellow); }
  .badge-adhoc     { background: #e0f7fa;              color: var(--unlock-teal); }
  .badge-new       { background: var(--blue-light);    color: var(--blue); }
  .badge-assigned  { background: var(--purple-light);  color: var(--purple); }
  .badge-inprogress{ background: var(--yellow-light);  color: var(--yellow); }
  .badge-resolved  { background: var(--green-light);   color: var(--green); }

  .status-select { border: none; background: transparent; font-size: 12px;
                   font-weight: 600; cursor: pointer; padding: 3px 4px; border-radius: 4px; }
  .status-select:focus { outline: 2px solid var(--blue); }

  .assignee-cell { white-space: nowrap; font-size: 12px; }
  .assignee-name { font-weight: 600; }
  .assignee-email { color: var(--muted); }

  .date-cell { white-space: nowrap; color: var(--muted); font-size: 12px; }
  .submitter-cell { font-size: 12px; color: var(--muted); }

  .empty-state { text-align: center; padding: 60px 20px; color: var(--muted); }
  .empty-state .icon { font-size: 40px; margin-bottom: 12px; }
  .error-banner { background: var(--red-light); color: var(--red); padding: 12px 32px;
                  font-size: 13px; font-weight: 500; }
</style>
</head>
<body>

<div class="header">
  <div>
    <h1>Badger Support — Ticket Dashboard</h1>
    <div class="subtitle">Investment Operations · Unlock Technologies</div>
  </div>
  <button class="refresh-btn" onclick="loadTickets()">↻ Refresh</button>
</div>

<div class="api-bar">
  <label>Agent URL:</label>
  <input type="text" id="apiUrl" placeholder="https://servicing-product-support-maria.unlock-bots.com"
         value="https://servicing-product-support-maria.unlock-bots.com" />
  <button onclick="loadTickets()">Connect</button>
</div>

<div id="errorBanner" class="error-banner" style="display:none"></div>

<!-- Summary stats -->
<div class="summary">
  <div class="card total">
    <div class="num" id="statTotal">—</div>
    <div class="lbl">Total Tickets</div>
  </div>
  <div class="card new">
    <div class="num" id="statNew">—</div>
    <div class="lbl">New</div>
  </div>
  <div class="card assigned">
    <div class="num" id="statAssigned">—</div>
    <div class="lbl">Assigned</div>
  </div>
  <div class="card inprogress">
    <div class="num" id="statInProgress">—</div>
    <div class="lbl">In Progress</div>
  </div>
  <div class="card resolved">
    <div class="num" id="statResolved">—</div>
    <div class="lbl">Resolved</div>
  </div>
</div>

<!-- Category breakdown -->
<div class="breakdown">
  <div class="cat-card badger">
    <div class="cat-name">Badger</div>
    <div class="cat-count" id="catBadger">—</div>
    <div class="cat-assignee">→ Jagat Shah</div>
  </div>
  <div class="cat-card excel">
    <div class="cat-name">Excel Toolkits</div>
    <div class="cat-count" id="catExcel">—</div>
    <div class="cat-assignee">→ Jagat Shah</div>
  </div>
  <div class="cat-card dealdata">
    <div class="cat-name">Deal Data Quality</div>
    <div class="cat-count" id="catDeal">—</div>
    <div class="cat-assignee">→ Brian Rubin</div>
  </div>
  <div class="cat-card adhoc">
    <div class="cat-name">Data Ad Hoc Request</div>
    <div class="cat-count" id="catAdhoc">—</div>
    <div class="cat-assignee">→ Jagat Shah</div>
  </div>
</div>

<!-- Filters -->
<div class="filters">
  <label>Filter:</label>
  <select id="filterCategory" onchange="renderTable()">
    <option value="">All Categories</option>
    <option>Badger</option>
    <option>Excel Toolkits</option>
    <option>Deal Data Quality</option>
    <option>Data Ad Hoc Request</option>
  </select>
  <select id="filterStatus" onchange="renderTable()">
    <option value="">All Statuses</option>
    <option>New</option>
    <option>Assigned</option>
    <option>In Progress</option>
    <option>Resolved</option>
  </select>
  <select id="filterAssignee" onchange="renderTable()">
    <option value="">All Assignees</option>
    <option>Jagat Shah</option>
    <option>Brian Rubin</option>
  </select>
  <input type="text" id="filterSearch" placeholder="Search description..."
         oninput="renderTable()" style="width:220px" />
  <button class="clear-btn" onclick="clearFilters()">Clear filters</button>
</div>

<!-- Table -->
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th>#</th>
        <th>Date</th>
        <th>Submitted By</th>
        <th>Description</th>
        <th>Category</th>
        <th>Assigned To</th>
        <th>Status</th>
      </tr>
    </thead>
    <tbody id="ticketBody">
      <tr><td colspan="7" class="empty-state">
        <div class="icon">📋</div>
        <div>Click Refresh to load tickets</div>
      </td></tr>
    </tbody>
  </table>
</div>

<script>
let allTickets = [];
const STATUSES = ["New", "Assigned", "In Progress", "Resolved"];

function getApiUrl() {
  return (document.getElementById('apiUrl').value || '').replace(/\/$/, '');
}

function showError(msg) {
  const el = document.getElementById('errorBanner');
  el.textContent = msg;
  el.style.display = msg ? 'block' : 'none';
}

async function loadTickets() {
  const url = getApiUrl();
  if (!url) { showError('Please enter the agent URL above.'); return; }
  showError('');
  try {
    const resp = await fetch(url + '/tickets');
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    allTickets = await resp.json();
    updateStats();
    renderTable();
  } catch (e) {
    showError('Could not load tickets: ' + e.message +
              '. Make sure the agent is running and the URL is correct.');
  }
}

function updateStats() {
  const t = allTickets;
  document.getElementById('statTotal').textContent     = t.length;
  document.getElementById('statNew').textContent       = t.filter(x => x.status === 'New').length;
  document.getElementById('statAssigned').textContent  = t.filter(x => x.status === 'Assigned').length;
  document.getElementById('statInProgress').textContent= t.filter(x => x.status === 'In Progress').length;
  document.getElementById('statResolved').textContent  = t.filter(x => x.status === 'Resolved').length;
  document.getElementById('catBadger').textContent     = t.filter(x => x.category === 'Badger').length;
  document.getElementById('catExcel').textContent      = t.filter(x => x.category === 'Excel Toolkits').length;
  document.getElementById('catDeal').textContent       = t.filter(x => x.category === 'Deal Data Quality').length;
  document.getElementById('catAdhoc').textContent      = t.filter(x => x.category === 'Data Ad Hoc Request').length;
}

function catClass(cat) {
  if (cat === 'Badger')              return 'badger';
  if (cat === 'Excel Toolkits')      return 'excel';
  if (cat === 'Deal Data Quality')   return 'dealdata';
  if (cat === 'Data Ad Hoc Request') return 'adhoc';
  return 'badger';
}

function statusClass(s) {
  return s.toLowerCase().replace(' ', '');
}

function formatDate(iso) {
  if (!iso) return '—';
  const d = new Date(iso + 'Z');
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
    + ' ' + d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

function renderTable() {
  const catF    = document.getElementById('filterCategory').value;
  const statF   = document.getElementById('filterStatus').value;
  const asnF    = document.getElementById('filterAssignee').value;
  const searchF = document.getElementById('filterSearch').value.toLowerCase();

  const filtered = allTickets.filter(t =>
    (!catF  || t.category === catF) &&
    (!statF || t.status   === statF) &&
    (!asnF  || t.assignee === asnF) &&
    (!searchF || t.description.toLowerCase().includes(searchF) ||
                 (t.sub_category||'').toLowerCase().includes(searchF))
  );

  const tbody = document.getElementById('ticketBody');
  if (!filtered.length) {
    tbody.innerHTML = `<tr><td colspan="7">
      <div class="empty-state"><div class="icon">🔍</div><div>No tickets match your filters.</div></div>
    </td></tr>`;
    return;
  }

  tbody.innerHTML = filtered.map(t => {
    const catLabel = t.sub_category ? `${t.category}<br><small style="color:#6b7280">${t.sub_category}</small>` : t.category;
    return `
    <tr>
      <td class="ticket-id">#${t.id}</td>
      <td class="date-cell">${formatDate(t.created_at)}</td>
      <td class="submitter-cell">${esc(t.submitted_by)}</td>
      <td class="desc-cell"><div class="desc-text" title="${esc(t.description)}">${esc(t.description)}</div></td>
      <td><span class="badge badge-${catClass(t.category)}">${catLabel}</span></td>
      <td class="assignee-cell">
        <div class="assignee-name">${esc(t.assignee)}</div>
        <div class="assignee-email">${esc(t.assignee_email)}</div>
      </td>
      <td>
        <select class="status-select badge badge-${statusClass(t.status)}"
                onchange="changeStatus(${t.id}, this)">
          ${STATUSES.map(s => `<option ${s === t.status ? 'selected' : ''}>${s}</option>`).join('')}
        </select>
      </td>
    </tr>`;
  }).join('');
}

async function changeStatus(ticketId, selectEl) {
  const newStatus = selectEl.value;
  const url = getApiUrl();
  try {
    const resp = await fetch(`${url}/tickets/${ticketId}/status`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status: newStatus}),
    });
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    // Update local state
    const t = allTickets.find(x => x.id === ticketId);
    if (t) t.status = newStatus;
    updateStats();
    renderTable();
  } catch (e) {
    showError('Failed to update status: ' + e.message);
    await loadTickets(); // revert by reloading
  }
}

function clearFilters() {
  document.getElementById('filterCategory').value = '';
  document.getElementById('filterStatus').value   = '';
  document.getElementById('filterAssignee').value = '';
  document.getElementById('filterSearch').value   = '';
  renderTable();
}

function esc(str) {
  return String(str || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Auto-load on page open
loadTickets();
</script>
</body>
</html>
