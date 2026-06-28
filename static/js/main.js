const menuButton = document.querySelector(".menu-btn");
const nav = document.querySelector("nav");
if (menuButton && nav) {
  menuButton.addEventListener("click", () => {
    const open = nav.classList.toggle("open");
    menuButton.setAttribute("aria-expanded", String(open));
  });
}

const toast = document.querySelector("#toast");
let toastTimer;
function showToast(message) {
  if (!toast) return;
  clearTimeout(toastTimer);
  toast.textContent = message;
  toast.classList.add("show");
  toastTimer = setTimeout(() => toast.classList.remove("show"), 1800);
}

setTimeout(() => {
  document.querySelectorAll(".flash").forEach(item => item.remove());
}, 2600);
