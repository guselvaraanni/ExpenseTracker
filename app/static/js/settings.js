/**
 * Settings page — category management.
 */

document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("category-modal");
  const form = document.getElementById("category-form");
  const addBtn = document.getElementById("btn-add-category");
  const tableBody = document.getElementById("categories-table-body");
  const loadingEl = document.getElementById("categories-loading");
  const emptyEl = document.getElementById("categories-empty");
  const tableWrap = document.getElementById("categories-table-wrap");
  const modalTitle = document.getElementById("category-modal-title");
  const categoryIdInput = document.getElementById("category-id");
  const nameInput = document.getElementById("category-name");
  const typeInput = document.getElementById("category-type");

  let categories = [];

  addBtn.addEventListener("click", () => openModal());
  form.addEventListener("submit", handleSubmit);

  modal.querySelectorAll("[data-close-modal]").forEach((el) => {
    el.addEventListener("click", closeModal);
  });

  loadCategories();

  async function loadCategories() {
    showLoading(true);
    try {
      const data = await AppUtils.fetchJSON("/api/v1/categories");
      categories = data.items || [];
      renderCategories();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    } finally {
      showLoading(false);
    }
  }

  function renderCategories() {
    tableBody.innerHTML = "";

    if (!categories.length) {
      emptyEl.classList.remove("hidden");
      tableWrap.classList.add("hidden");
      return;
    }

    emptyEl.classList.add("hidden");
    tableWrap.classList.remove("hidden");

    categories.forEach((category) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${escapeHtml(category.name)}</td>
        <td><span class="badge badge-${category.type}">${capitalize(category.type)}</span></td>
        <td class="col-actions">
          <button type="button" class="btn btn-sm btn-secondary" data-edit="${category.id}">Edit</button>
          <button type="button" class="btn btn-sm btn-danger" data-delete="${category.id}">Delete</button>
        </td>
      `;
      tableBody.appendChild(row);
    });

    tableBody.querySelectorAll("[data-edit]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const category = categories.find((item) => item.id === Number(btn.dataset.edit));
        if (category) {
          openModal(category);
        }
      });
    });

    tableBody.querySelectorAll("[data-delete]").forEach((btn) => {
      btn.addEventListener("click", () => deleteCategory(Number(btn.dataset.delete)));
    });
  }

  function openModal(category = null) {
    if (category) {
      modalTitle.textContent = "Edit Category";
      categoryIdInput.value = String(category.id);
      nameInput.value = category.name;
      typeInput.value = category.type;
    } else {
      modalTitle.textContent = "Add Category";
      categoryIdInput.value = "";
      nameInput.value = "";
      typeInput.value = "expense";
    }
    modal.classList.remove("hidden");
    modal.setAttribute("aria-hidden", "false");
    nameInput.focus();
  }

  function closeModal() {
    modal.classList.add("hidden");
    modal.setAttribute("aria-hidden", "true");
    form.reset();
    categoryIdInput.value = "";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    const payload = {
      name: nameInput.value.trim(),
      type: typeInput.value,
    };
    const categoryId = categoryIdInput.value;

    try {
      if (categoryId) {
        await AppUtils.fetchJSON(`/api/v1/categories/${categoryId}`, {
          method: "PUT",
          body: JSON.stringify(payload),
        });
        AppUtils.showToast("Category updated.", "success");
      } else {
        await AppUtils.fetchJSON("/api/v1/categories", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        AppUtils.showToast("Category created.", "success");
      }
      closeModal();
      await loadCategories();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    }
  }

  async function deleteCategory(categoryId) {
    const category = categories.find((item) => item.id === categoryId);
    if (!category) {
      return;
    }

    const confirmed = window.confirm(`Delete category "${category.name}"?`);
    if (!confirmed) {
      return;
    }

    try {
      await AppUtils.fetchJSON(`/api/v1/categories/${categoryId}`, {
        method: "DELETE",
      });
      AppUtils.showToast("Category deleted.", "success");
      await loadCategories();
    } catch (error) {
      AppUtils.showToast(error.message, "error");
    }
  }

  function showLoading(isLoading) {
    loadingEl.classList.toggle("hidden", !isLoading);
    if (isLoading) {
      emptyEl.classList.add("hidden");
      tableWrap.classList.add("hidden");
    }
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
