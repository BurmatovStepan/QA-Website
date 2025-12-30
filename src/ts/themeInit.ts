const THEME_CLASS = "theme-light";
const THEME_STORAGE_KEY = "user-theme";

const LIGHT_ICON_PATH: string = "/static/assets/light-theme.svg";
const DARK_ICON_PATH: string = "/static/assets/dark-theme.svg";


function initTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch__icon") as HTMLImageElement;

    const preferredTheme = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    // TODO Add theme to settings,
    if (icon && preferredTheme === "light") {
        icon.src = DARK_ICON_PATH;
    } else if (icon) {
        icon.src = LIGHT_ICON_PATH;
    }

    if (preferredTheme === "light") {
        body.classList.add(THEME_CLASS);
    }

    const themeSwitch = document.querySelector(".js-theme-switch")
    if (themeSwitch) {
        themeSwitch.addEventListener("click", toggleTheme);
        themeSwitch.addEventListener("keydown", themeSwitchKeyboardHandler);
    }
}


function toggleTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch__icon") as HTMLImageElement;

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

document.addEventListener("DOMContentLoaded", initTheme);
