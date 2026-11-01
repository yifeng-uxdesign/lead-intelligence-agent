import { mountWidget } from "./widget.js";

const widget = mountWidget(document.getElementById("ns-widget-root"));

function openAgent(event) {
  if (event) event.preventDefault();
  widget.open();
}

document.querySelectorAll("[data-open-widget]").forEach((node) => {
  node.addEventListener("click", openAgent);
});

const navToggle = document.querySelector("[data-nav-toggle]");
const nav = document.querySelector("[data-nav]");
navToggle?.addEventListener("click", () => {
  const expanded = navToggle.getAttribute("aria-expanded") === "true";
  navToggle.setAttribute("aria-expanded", String(!expanded));
  nav.classList.toggle("is-open", !expanded);
});

nav?.querySelectorAll("a").forEach((link) => {
  link.addEventListener("click", () => {
    nav.classList.remove("is-open");
    navToggle?.setAttribute("aria-expanded", "false");
  });
});
