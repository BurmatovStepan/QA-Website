const THEME_CLASS = "theme-light";
const THEME_STORAGE_KEY = "user-theme";

const LIGHT_ICON_PATH: string = "/static/assets/light-theme.svg";
const DARK_ICON_PATH: string = "/static/assets/dark-theme.svg";
const DEFAULT_AVATAR_PATH: string = "/static/assets/avatar.svg";
const INVALID_FILE_ICON_PATH: string = "/static/assets/invalid-file.svg";

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


function initTheme(): void {
    const body = document.body;
    const icon = document.querySelector(".js-theme-switch__icon") as HTMLImageElement;

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

class CustomFileInput {
    private initialFileName: string;

    private constructor(
        private fileNameDisplay: HTMLSpanElement,
        private filePreview: HTMLImageElement,
        private fileResetButton: HTMLDivElement,
        private fileClearButton: HTMLButtonElement,
        private fileInput: HTMLInputElement,
        private fileClearInput: HTMLInputElement
    ) {
        try {
            const urlObject = new URL(filePreview.src);
            this.initialFileName = urlObject.pathname;
        } catch (e) {
            this.initialFileName = filePreview.src;
        }

        fileInput.addEventListener("change", this.fileChangeHandler);

        fileResetButton.addEventListener("click", this.resetFile);
        fileResetButton.addEventListener("keydown", this.resetFileKeyboardHandler);

        fileClearButton.addEventListener("click", this.clearFile);
        fileClearButton.addEventListener("keydown", this.clearFileKeyboardHandler);
    }

    private fileChangeHandler = (event: Event): void => {
        const file = this.fileInput.files ? this.fileInput.files[0] : null;

        if (file) {
            this.fileClearInput.value = "False";
            this.filePreview.classList.remove("themed-contrast")
        }

        this.updateFileNameDisplay(file.name);
        this.updateFilePreview(file);
    }

    private updateFileNameDisplay = (fileName: string | null): void => {
        if (fileName) {
            this.fileNameDisplay.textContent = fileName
        } else {
            this.fileNameDisplay.textContent = "No file selected"
        }
    }

    private updateFilePreview = (file: File | string | null): void => {
        if (file === null) {
            this.filePreview.src = DEFAULT_AVATAR_PATH;
            this.filePreview.classList.add("themed-contrast")
        }

        if (file instanceof File && !file.type.startsWith("image/")) {
            this.filePreview.src = INVALID_FILE_ICON_PATH;
            this.filePreview.classList.add("themed-contrast")
        }

        if (file instanceof File && file.type.startsWith("image/")) {
            const reader = new FileReader()

            const updateFilePreview = (event: ProgressEvent<FileReader>): void =>  {
                if (event.target && event.target.result && this.filePreview) {
                    this.filePreview.src = event.target.result as string;
                }
            }
            reader.onload = updateFilePreview;

            reader.readAsDataURL(file);
        }
        if (typeof(file) === "string") {
            this.filePreview.src = file;
            console.log({file, DEFAULT_AVATAR_PATH})
            if (file === DEFAULT_AVATAR_PATH) {
                this.filePreview.classList.add("themed-contrast");
            } else {
                this.filePreview.classList.remove("themed-contrast");
            }
        }
    }

    private resetFile = (): void => {
        this.fileClearInput.value = "False";
        this.fileInput.value = "";
        this.updateFileNameDisplay("No file selected");
        this.updateFilePreview(this.initialFileName);
    }

    private resetFileKeyboardHandler = (event: KeyboardEvent): void => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            this.resetFile();
        }
    }

    private clearFile = (): void => {
        this.fileClearInput.value = "True";
        this.fileInput.value = "";
        this.updateFileNameDisplay("Default avatar");
        this.updateFilePreview(null);
    }

    private clearFileKeyboardHandler = (event: KeyboardEvent): void => {
        if (event.key === "Enter" || event.key === " ") {
            event.preventDefault();
            this.clearFile();
        }
    }

    static create = (): CustomFileInput | null => {
        const fileNameDisplay = document.querySelector(".js-file-input-filename");
        const filePreview = document.querySelector(".js-file-input-preview");
        const fileResetButton = document.querySelector(".js-file-input-reset-button")
        const fileClearButton = document.querySelector(".js-file-input-clear-button")
        const fileInput = document.querySelector(".js-file-input-input");
        const fileClearInput = document.querySelector(".js-file-input-clear-input");

        if (fileNameDisplay instanceof HTMLSpanElement &&
            filePreview instanceof HTMLImageElement &&
            fileResetButton instanceof HTMLDivElement &&
            fileClearButton instanceof HTMLButtonElement &&
            fileInput instanceof HTMLInputElement &&
            fileClearInput instanceof HTMLInputElement

        ) {
            return new CustomFileInput(fileNameDisplay, filePreview, fileResetButton, fileClearButton, fileInput, fileClearInput);
        }
        console.error("Fields required for CustomFileInput are missing")
        return null;
    }

}

document.addEventListener("DOMContentLoaded", checkActiveTab);
document.addEventListener("DOMContentLoaded", initTheme);
CustomFileInput.create()
