const THEME_CLASS = "theme-light";
const THEME_STORAGE_KEY = "user-theme";

const LIGHT_ICON_PATH: string = require("../assets/light-theme.svg");
const DARK_ICON_PATH: string = require("../assets/dark-theme.svg");


function checkActiveTab(): void {
    let currentPath = window.location.pathname;

    const navLinks = document.querySelectorAll(".js-pages-list a");

    for (let i = 0; i < navLinks.length; ++i) {
        const link = navLinks[i];

        if (link.getAttribute("href") === currentPath) {
            const listItem = link.closest(".navigation__page-link");

            if (listItem) {
                listItem.classList.add("navigation__page-link--current");
            }
            return;
        }
    }
}


function toggleTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch-icon") as HTMLImageElement;

    body.classList.toggle(THEME_CLASS);

    const isLight = body.classList.contains(THEME_CLASS);

    if (icon) {
        icon.src = isLight ? DARK_ICON_PATH : LIGHT_ICON_PATH;
    }
    localStorage.setItem(THEME_STORAGE_KEY, isLight ? "light" : "dark");
}


function themeSwitchKeyboardHandler(event: KeyboardEvent): void {
    if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleTheme();
    }
}


function initTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch-icon") as HTMLImageElement;

    const savedTheme = localStorage.getItem(THEME_STORAGE_KEY);

    if (icon && savedTheme === "light") {
        icon.src = DARK_ICON_PATH;
    } else if (icon) {
        icon.src = LIGHT_ICON_PATH;
    }

    if (savedTheme === "light") {
        body.classList.add(THEME_CLASS);
    }

    const themeSwitch = document.querySelector(".js-theme-switch")
    if (themeSwitch) {
        themeSwitch.addEventListener("click", toggleTheme);
        themeSwitch.addEventListener("keydown", themeSwitchKeyboardHandler);
    }
}


document.addEventListener("DOMContentLoaded", checkActiveTab);
document.addEventListener("DOMContentLoaded", initTheme);
