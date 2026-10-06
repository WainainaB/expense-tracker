const API = "http://localhost:8000";

const $ = (id) => document.getElementById(id);
const form = $("expense-form");
const messageEl = $("message");

function showMessage(text, type = "success") {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
  if (text) setTimeout(() => { messageEl.textContent = ""; }, 3000);
}

async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const msg = Array.isArray(data?.detail)
      ? data.detail.map(d => `${d.loc?.join(".")}: ${d.msg}`).join(", ")
      : data?.detail || "Request failed";
    throw new Error(msg);
  }
  return data;
}

async function loadExpenses() {
  const params = new URLSearchParams();
  const cat = $("filter-category").value.trim();
  if (cat) params.set("category", cat);
  params.set("sort_by", $("sort-by").value);
  params.set("order", $("order").value);

  const expenses = await api(`/expenses?${params}`);
  const tbody = document.querySelector("#expenses-table tbody");
  tbody.innerHTML = "";

  if (!expenses.length) {
    tbody.innerHTML = `<tr><td colspan="6" class="empty">No expenses yet.</td></tr>`;
    return;
  }

  for (const e of expenses) {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${e.date}</td>
      <td>${escapeHtml(e.description)}</td>
      <td>${escapeHtml(e.category)}</td>
      <td>$${e.amount.toFixed(2)}</td>
      <td>${escapeHtml(e.paid_by)}</td>
      <td>
        <button data-action="edit" data-id="${e.id}">Edit</button>
        <button data-action="delete" data-id="${e.id}" class="danger">Delete</button>
      </td>`;
    tbody.appendChild(tr);
  }
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function loadSummary() {
  const data = await api("/summary");

  const catBody = document.querySelector("#summary-category tbody");
  catBody.innerHTML = data.by_category
    .map(r => `<tr><td>${escapeHtml(r.category)}</td><td>$${r.total.toFixed(2)}</td></tr>`)
    .join("") || `<tr><td colspan="2" class="empty">No data</td></tr>`;

  const personBody = document.querySelector("#summary-person tbody");
  personBody.innerHTML = data.by_person
    .map(r => `<tr><td>${escapeHtml(r.paid_by)}</td><td>$${r.total.toFixed(2)}</td></tr>`)
    .join("") || `<tr><td colspan="2" class="empty">No data</td></tr>`;
}

form.addEventListener("submit", async (ev) => {
  ev.preventDefault();
  const id = $("expense-id").value;
  const payload = {
    description: $("description").value.trim(),
    amount: parseFloat($("amount").value),
    category: $("category").value.trim(),
    date: $("date").value,
    paid_by: $("paid_by").value.trim(),
  };

  if (!payload.description) return showMessage("Description is required", "error");
  if (!(payload.amount > 0)) return showMessage("Amount must be greater than 0", "error");
  if (!payload.category) return showMessage("Category is required", "error");
  if (!payload.date) return showMessage("Date is required", "error");
  if (!payload.paid_by) return showMessage("Paid by is required", "error");

  try {
    if (id) {
      await api(`/expenses/${id}`, { method: "PATCH", body: JSON.stringify(payload) });
      showMessage("Expense updated");
    } else {
      await api("/expenses", { method: "POST", body: JSON.stringify(payload) });
      showMessage("Expense added");
    }
    resetForm();
    await Promise.all([loadExpenses(), loadSummary()]);
  } catch (err) {
    showMessage(err.message, "error");
  }
});

function resetForm() {
  form.reset();
  $("expense-id").value = "";
  $("form-title").textContent = "Add Expense";
  $("submit-btn").textContent = "Save";
  $("cancel-btn").hidden = true;
}

$("cancel-btn").addEventListener("click", resetForm);

document.querySelector("#expenses-table").addEventListener("click", async (ev) => {
  const btn = ev.target.closest("button[data-action]");
  if (!btn) return;
  const id = btn.dataset.id;

  if (btn.dataset.action === "delete") {
    if (!confirm("Delete this expense?")) return;
    try {
      await api(`/expenses/${id}`, { method: "DELETE" });
      showMessage("Expense deleted");
      await Promise.all([loadExpenses(), loadSummary()]);
    } catch (err) {
      showMessage(err.message, "error");
    }
  }

  if (btn.dataset.action === "edit") {
    const all = await api("/expenses");
    const e = all.find(x => x.id == id);
    if (!e) return;
    $("expense-id").value = e.id;
    $("description").value = e.description;
    $("amount").value = e.amount;
    $("category").value = e.category;
    $("date").value = e.date;
    $("paid_by").value = e.paid_by;
    $("form-title").textContent = "Edit Expense";
    $("submit-btn").textContent = "Update";
    $("cancel-btn").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
});

$("refresh-btn").addEventListener("click", loadExpenses);
$("filter-category").addEventListener("input", debounce(loadExpenses, 300));
$("sort-by").addEventListener("change", loadExpenses);
$("order").addEventListener("change", loadExpenses);

function debounce(fn, ms) {
  let t;
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), ms); };
}

loadExpenses();
loadSummary();