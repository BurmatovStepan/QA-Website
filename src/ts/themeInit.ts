const THEME_CLASS = "theme-light";
const THEME_STORAGE_KEY = "user-theme";

const SUN_ICON_PATH: string = "url('/static/assets/sun-icon.svg')";
const MOON_ICON_PATH: string = "url('/static/assets/moon-icon.svg')";


function initTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch-icon") as HTMLDivElement;

    const preferredTheme = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
    // TODO Add theme to settings,
    if (icon && preferredTheme === "light") {
        icon.style.maskImage = MOON_ICON_PATH;

    } else if (icon) {
        icon.style.maskImage = SUN_ICON_PATH;
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
    const icon = document.querySelector(".js-theme-switch-icon") as HTMLDivElement;

    body.classList.toggle(THEME_CLASS);

    const isLight = body.classList.contains(THEME_CLASS);

    if (icon) {
        icon.style.maskImage = isLight ? MOON_ICON_PATH : SUN_ICON_PATH;
    }
}


function themeSwitchKeyboardHandler(event: KeyboardEvent): void {
    if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleTheme();
    }
}

document.addEventListener("DOMContentLoaded", initTheme);
