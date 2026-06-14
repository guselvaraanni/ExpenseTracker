/**
 * Shared frontend utilities.
 */

const AppUtils = {
  /**
   * Show a toast notification.
   */
  showToast(message, type = "info") {
    const container = document.getElementById("toast-container");
    if (!container) {
      console.log(`[${type}] ${message}`);
      return;
    }

    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => toast.remove(), 3500);
  },

  /**
   * JSON fetch helper with error handling.
   */
  async fetchJSON(url, options = {}) {
    const response = await fetch(url, {
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });

    if (response.status === 204) {
      return null;
    }

    let payload = null;
    const contentType = response.headers.get("content-type") || "";
    if (contentType.includes("application/json")) {
      payload = await response.json();
    }

    if (!response.ok) {
      const detail = payload && payload.detail ? payload.detail : `Request failed: ${response.status}`;
      throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
    }

    return payload;
  },
};

window.AppUtils = AppUtils;
