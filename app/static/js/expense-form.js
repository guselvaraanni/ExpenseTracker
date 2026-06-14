/**
 * Expense form — create, list, edit, and delete transactions.
 */

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("transaction-form");
  const editForm = document.getElementById("transaction-edit-form");
  const modal = document.getElementById("transaction-modal");
  const typeSelect = document.getElementById("transaction-type");
  const categorySelect = document.getElementById("transaction-category");
  const dateInput = document.getElementById("transaction-date");
  const filterType = document.getElementById("filter-type");
  const tableBody = document.getElementById("transactions-table-body");
  const loadingEl = document.getElementById("transactions-loading");
  const emptyEl = document.getElementById("transactions-empty");
  const tableWrap = document.getElementById("transactions-table-wrap");
  const paginationEl = document.getElementById("transactions-pagination");

  const editTypeSelect = document.getElementById("edit-transaction-type");
  const editCategorySelect = document.getElementById("edit-transaction-category");
  const editIdInput = document.getElementById("edit-transaction-id");
  const editAmountInput = document.getElementById("edit-transaction-amount");
  const editDateInput = document.getElementById("edit-transaction-date");
  const editDescriptionInput = document.getElementById("edit-transaction-description");

  let categories = [];
  let currentPage = 1;
  const perPage = 10;

  dateInput.value = todayIso();
  typeSelect.addEventListener("change", () => populateCategorySelect(categorySelect, typeSelect.value));
  editTypeSelect.addEventListener("change", () => populateCategorySelect(editCategorySelect, editTypeSelect.value));
  filterType.addEventListener("change", () => {
    currentPage = 1;
    loadTransactions();
  });
  form.addEventListener("submit", handleCreate);
  editForm.addEventListener("submit", handleUpdate);

  modal.querySelectorAll("[data-close-modal]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  init();

  async function init() {
    try {
      const data = await AppUtils.fetchJSON("/api/v1/categories");
      categories = data.items || [];
      populateCategorySelect(categorySelect, typeSelect.value);
      await loadTransactions();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
      showTransactionsLoading(false);
    }
  }

  async function loadTransactions() {
    showTransactionsLoading(true);
    const typeParam = filterType.value !== "all" ? `&type=${filterType.value}` : "";
    const url = `/api/v1/transactions?page=${currentPage}&per_page=${perPage}${typeParam}`;

    try {
      const data = await AppUtils.fetchJSON(url);
      renderTransactions(data);
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    } finally {
      showTransactionsLoading(false);
    }
  }

  function renderTransactions(data) {
    tableBody.innerHTML = "";
    const items = data.items || [];

    if (!items.length) {
      emptyEl.classList.remove("hidden");
      tableWrap.classList.add("hidden");
      paginationEl.innerHTML = "";
      return;
    }

    emptyEl.classList.add("hidden");
    tableWrap.classList.remove("hidden");

    items.forEach((transaction) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${transaction.transaction_date}</td>
        <td>${escapeHtml(transaction.description)}</td>
        <td>${escapeHtml(transaction.category_name)}</td>
        <td><span class="badge badge-${transaction.category_type}">${capitalize(transaction.category_type)}</span></td>
        <td class="col-amount">${formatAmount(transaction.amount, transaction.category_type)}</td>
        <td class="col-actions">
          <button type="button" class="btn btn-sm btn-secondary" data-edit="${transaction.id}">Edit</button>
          <button type="button" class="btn btn-sm btn-danger" data-delete="${transaction.id}">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    tableBody.querySelectorAll("[data-edit]").forEach((btn) => {
      btn.addEventListener("click", () => openEditModal(Number(btn.dataset.edit), items));
    });

    tableBody.querySelectorAll("[data-delete]").forEach((btn) => {
      btn.addEventListener("click", () => deleteTransaction(Number(btn.dataset.delete)));
    });

    renderPagination(data);
  }

  function renderPagination(data) {
    paginationEl.innerHTML = "";
    if (data.pages <= 1) {
      return;
    }

    const prev = document.createElement("button");
    prev.type = "button";
    prev.className = "btn btn-sm btn-secondary";
    prev.textContent = "Previous";
    prev.disabled = data.page <= 1;
    prev.addEventListener("click", () => {
      currentPage -= 1;
      loadTransactions();
    });

    const next = document.createElement("button");
    next.type = "button";
    next.className = "btn btn-sm btn-secondary";
    next.textContent = "Next";
    next.disabled = data.page >= data.pages;
    next.addEventListener("click", () => {
      currentPage += 1;
      loadTransactions();
    });

    const label = document.createElement("span");
    label.className = "pagination-label";
    label.textContent = `Page ${data.page} of ${data.pages}`;

    paginationEl.appendChild(prev);
    paginationEl.appendChild(label);
    paginationEl.appendChild(next);
  }

  async function handleCreate(event) {
    event.preventDefault();
    const payload = {
      amount: document.getElementById("transaction-amount").value,
      description: document.getElementById("transaction-description").value.trim(),
      transaction_date: dateInput.value,
      category_id: Number(categorySelect.value),
    };

    try {
      await AppUtils.fetchJSON("/api/v1/transactions", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      AppUtils.showToast("Transaction saved.", "success");
      form.reset();
      dateInput.value = todayIso();
      populateCategorySelect(categorySelect, typeSelect.value);
      currentPage = 1;
      await loadTransactions();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    }
  }

  function openEditModal(transactionId, items) {
    const transaction = items.find((item) => item.id === transactionId);
    if (!transaction) {
      return;
    }

    editIdInput.value = String(transaction.id);
    editTypeSelect.value = transaction.category_type;
    populateCategorySelect(editCategorySelect, transaction.category_type, transaction.category_id);
    editAmountInput.value = transaction.amount;
    editDateInput.value = transaction.transaction_date;
    editDescriptionInput.value = transaction.description;

    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
  }

  function closeModal() {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    editForm.reset();
    editIdInput.value = "";
  }

  async function handleUpdate(event) {
    event.preventDefault();
    const transactionId = editIdInput.value;
    const payload = {
      amount: editAmountInput.value,
      description: editDescriptionInput.value.trim(),
      transaction_date: editDateInput.value,
      category_id: Number(editCategorySelect.value),
    };

    try {
      await AppUtils.fetchJSON(`/api/v1/transactions/${transactionId}`, {
        method: "PUT",
        body: JSON.stringify(payload),
      });
      AppUtils.showToast("Transaction updated.", "success");
      closeModal();
      await loadTransactions();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    }
  }

  async function deleteTransaction(transactionId) {
    const confirmed = window.confirm("Delete this transaction?");
    if (!confirmed) {
      return;
    }

    try {
      await AppUtils.fetchJSON(`/api/v1/transactions/${transactionId}`, {
        method: "DELETE",
      });
      AppUtils.showToast("Transaction deleted.", "success");
      await loadTransactions();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    }
  }

  function populateCategorySelect(selectEl, type, selectedId = null) {
    const filtered = categories.filter((category) => category.type === type);
    selectEl.innerHTML = '<option value="">Select category…</option>';
    filtered.forEach((category) => {
      const option = document.createElement("option");
      option.value = String(category.id);
      option.textContent = category.name;
      if (selectedId && category.id === selectedId) {
        option.selected = true;
      }
      selectEl.appendChild(option);
    });
  }

  function showTransactionsLoading(isLoading) {
    loadingEl.classList.toggle("hidden", !isLoading);
    if (isLoading) {
      emptyEl.classList.add("hidden");
      tableWrap.classList.add("hidden");
    }
  }

  function todayIso() {
    return new Date().toISOString().slice(0, 10);
  }

  function formatAmount(amount, type) {
    const prefix = type === "income" ? "+" : "-";
    return `${prefix}$${Number(amount).toFixed(2)}`;
  }

  function capitalize(value) {
    return value.charAt(0).toUpperCase() + value.slice(1);
  }

  function escapeHtml(value) {
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }
});
