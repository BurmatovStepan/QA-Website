var THEME_CLASS = "theme-light";
var THEME_STORAGE_KEY = "user-theme";
var LIGHT_ICON_PATH = "static/assets/light-theme.svg";
var DARK_ICON_PATH = "static/assets/dark-theme.svg";
function checkActiveTab() {
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll(".js-pages-list a");
    for (var i = 0; i < navLinks.length; ++i) {
        var link = navLinks[i];
        if (link.getAttribute("href") === currentPath) {
            var listItem = link.closest(".navigation__page-link");
            if (listItem) {
                listItem.classList.add("navigation__page-link--current");
            }
            return;
        }
    }
}
function initTheme() {
    var body = document.body;
    var icon = document.querySelector(".js-theme-switch-icon");
    var savedTheme = localStorage.getItem(THEME_STORAGE_KEY);
    if (icon && savedTheme === "light") {
        icon.src = DARK_ICON_PATH;
    }
    else if (icon) {
        icon.src = LIGHT_ICON_PATH;
    }
    if (savedTheme === "light") {
        body.classList.add(THEME_CLASS);
    }
    var themeSwitch = document.querySelector(".js-theme-switch");
    if (themeSwitch) {
        themeSwitch.addEventListener("click", toggleTheme);
        themeSwitch.addEventListener("keydown", themeSwitchKeyboardHandler);
    }
}
function toggleTheme() {
    var body = document.body;
    var icon = document.querySelector(".js-theme-switch-icon");
    body.classList.toggle(THEME_CLASS);
    var isLight = body.classList.contains(THEME_CLASS);
    if (icon) {
        icon.src = isLight ? DARK_ICON_PATH : LIGHT_ICON_PATH;
    }
    localStorage.setItem(THEME_STORAGE_KEY, isLight ? "light" : "dark");
}
function themeSwitchKeyboardHandler(event) {
    if (event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        toggleTheme();
    }
}
function initCustomFileInput() {
    var fileInput = document.querySelector(".js-file-input");
    if (fileInput) {
        fileInput.addEventListener("change", updateFileName);
    }
}
function updateFileName(event) {
    var fileNameDisplay = document.querySelector(".js-file-input-filename");
    var input = event.target;
    var file = input.files ? input.files[0] : null;
    fileNameDisplay.textContent = file ? file.name : "No file selected";
}
document.addEventListener("DOMContentLoaded", checkActiveTab);
document.addEventListener("DOMContentLoaded", initTheme);
document.addEventListener("DOMContentLoaded", initCustomFileInput);
