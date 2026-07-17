/**
 * AI-Powered Smart Recipe Generator — Main JavaScript
 * MAEC258 | RVITM MCA | A.Y 2025-2026
 */
"use strict";

/* ── Navbar Scroll Effect ──────────────────────────────────────── */
window.addEventListener("scroll", () => {
  const nav = document.getElementById("mainNav");
  if (nav) {
    nav.style.boxShadow = window.scrollY > 40
      ? "0 4px 28px rgba(0,0,0,.4)"
      : "0 2px 20px rgba(0,0,0,.25)";
  }
});

/* ── Bootstrap Tooltips ────────────────────────────────────────── */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('[data-bs-toggle="tooltip"]')
    .forEach(el => new bootstrap.Tooltip(el));
});

/* ── Auto-dismiss Flash Messages ───────────────────────────────── */
setTimeout(() => {
  document.querySelectorAll(".alert").forEach(a => {
    try { bootstrap.Alert.getOrCreateInstance(a).close(); } catch(e) {}
  });
}, 4000);

/* ── Animate Ingredient Match Bars on Results Page ─────────────── */
window.addEventListener("load", () => {
  document.querySelectorAll(".match-bar-fill").forEach(bar => {
    const w = bar.style.width;
    bar.style.width = "0%";
    setTimeout(() => { bar.style.width = w; }, 300);
  });
  document.querySelectorAll(".nutr-fill").forEach(bar => {
    const w = bar.style.width;
    bar.style.width = "0%";
    setTimeout(() => { bar.style.width = w; }, 400);
  });
});

/* ── Grocery Order Helper ──────────────────────────────────────── */
function orderGrocery(ingredients, platform) {
  fetch("/api/order", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ingredients, platform })
  })
  .then(r => r.json())
  .then(data => {
    if (data.status === "success") window.open(data.order_url, "_blank");
    else alert("Could not place order. Please try again.");
  })
  .catch(() => alert("Connection error. Please try again."));
}
