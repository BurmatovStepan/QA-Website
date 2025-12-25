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

function checkDjangoMessages(): void {
    const messageElements = document.querySelectorAll("#js-django-messages .js-django-message");

    const result = Array.from(messageElements).reduce(
        (acc, value: HTMLSpanElement) => {
            acc.messages.push(value.textContent);

            if (value.dataset.type === "error") {
                acc.type = "error";
            }

            return acc;
        },
        { messages: [] as string[], type: "success"}
    );

    if (result.messages.length) {
        Toaster.makeToast(result.messages, result.type);
    }
}

class CustomFileInput {
    private initialFileName: string | null;

    private constructor(
        private fileInput: HTMLInputElement,
        private fileNameDisplay: HTMLSpanElement,
        private filePreview: HTMLImageElement | null,
        private fileResetButton: HTMLDivElement | null,
        private fileClearButton: HTMLButtonElement | null,
        private fileClearInput: HTMLInputElement | null
    ) {
        fileInput.addEventListener("change", this.fileChangeHandler);

        if (filePreview) {
            try {
                const urlObject = new URL(filePreview.src);
                this.initialFileName = urlObject.pathname;
            } catch (e) {
                this.initialFileName = filePreview.src;
            }
        } else {
            this.initialFileName = null;
        }

        if (fileResetButton) {
            fileResetButton.addEventListener("click", this.resetFile);
            fileResetButton.addEventListener("keydown", this.resetFileKeyboardHandler);
        }

        if (fileClearButton) {
            fileClearButton.addEventListener("click", this.clearFile);
            fileClearButton.addEventListener("keydown", this.clearFileKeyboardHandler);
        }
    }

    private fileChangeHandler = (event: Event): void => {
        const file = this.fileInput.files ? this.fileInput.files[0] : null;

        if (file) {
            if (this.fileClearInput) {
                this.fileClearInput.value = "False";
            }
            if (this.filePreview) {
                this.filePreview.classList.remove("themed-contrast")
            }

            this.updateFileNameDisplay(file.name);
            this.updateFilePreview(file);
        } else {
            this.updateFileNameDisplay(null);
            this.updateFilePreview(null);
        }
    }

    private updateFileNameDisplay = (fileName: string | null): void => {
        if (fileName) {
            this.fileNameDisplay.textContent = fileName
        } else {
            this.fileNameDisplay.textContent = "No file selected"
        }
    }

    private updateFilePreview = (file: File | string | null): void => {
        if (!this.filePreview) {
            return;
        }

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

            if (file === DEFAULT_AVATAR_PATH) {
                this.filePreview.classList.add("themed-contrast");
            } else {
                this.filePreview.classList.remove("themed-contrast");
            }
        }
    }

    private resetFile = (): void => {
        if (this.fileClearInput) {
            this.fileClearInput.value = "False";
        }

        this.fileInput.value = "";
        this.updateFileNameDisplay(null);
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
        const fileInput = document.querySelector(".js-file-input-input");
        const fileNameDisplay = document.querySelector(".js-file-input-filename");

        const filePreview = document.querySelector(".js-file-input-preview");
        const fileResetButton = document.querySelector(".js-file-input-reset-button")
        const fileClearButton = document.querySelector(".js-file-input-clear-button")
        const fileClearInput = document.querySelector(".js-file-input-clear-input");

        if (!(fileInput instanceof HTMLInputElement) || !(fileNameDisplay instanceof HTMLSpanElement)) {
            console.error("Crucial elements required for CustomFileInput are missing or wrong type");
            return null;
        }

        const validFilePreview = (filePreview instanceof HTMLImageElement) ? filePreview : null;
        const validFileResetButton = (fileResetButton instanceof HTMLDivElement) ? fileResetButton : null;
        const validFileClearButton = (fileClearButton instanceof HTMLButtonElement) ? fileClearButton : null;
        const validFileClearInput = (fileClearInput instanceof HTMLInputElement) ? fileClearInput : null;

        return new CustomFileInput(
            fileInput,
            fileNameDisplay,
            validFilePreview,
            validFileResetButton,
            validFileClearButton,
            validFileClearInput
        );
    }
}


class NewAnswerHandler {
    private pageSize: number;

    private constructor(
        private form: HTMLFormElement,
        private answersSection: HTMLElement,
        private answerContent: HTMLTextAreaElement,
        private submitButton: HTMLButtonElement
    ) {
        form.addEventListener("submit", this.formSubmitHandler)
        this.pageSize = +this.answersSection.dataset.pageSize;
    }

    // TODO add pagination button
    private formSubmitHandler = async (event: Event): Promise<void> => {
        event.preventDefault();
        this.clearErrors();

        const content = this.answerContent.value.trim()
        if (!content) {
            return;
        }

        this.submitButton.disabled = true;
        this.submitButton.textContent = "Submitting...";

        const formData = new FormData(this.form)
        try {
            const response = await fetch(this.form.action, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                },
                body: formData
            });

            const contentType = response.headers.get("content-type");
            const isJsonResponse = contentType && contentType.includes("application/json");

            if (response.status === 404 && !isJsonResponse) {
                const synthetic_error = {
                    "__all__": ["The submission endpoint was not found. Please reload the page."]
                }
                this.displayErrors(synthetic_error)
                return;
            }

            const result = await response.json()

            if (response.ok) {
                this.answerContent.value = "";
                this.answersSection.insertAdjacentHTML("afterbegin", result.answer_html);

                const answerElements = this.answersSection.querySelectorAll(".js-answer-card");
                if (this.pageSize && answerElements.length > this.pageSize) {
                    const lastAnswer = answerElements[answerElements.length - 1];
                    lastAnswer.remove();
                }

            } else {
                if (result.error_type === "validation_error") {
                    this.displayErrors(result.errors);

                } else if (["authentication_required", "question_not_found"].includes(result.error_type)) {
                    const errorWrapper = this.form.querySelector(".form__error-wrapper--non-field");
                    if (errorWrapper) {
                        const errorHtml = `<span class="form__error-message">${result.message}</span>`;
                        errorWrapper.insertAdjacentHTML("beforeend", errorHtml);
                    }
                }
            }

        } catch (error) {
            console.error("Network or unexpected error:", error);
            Toaster.makeToast(["A network error occurred."], "error");

        } finally {
            this.submitButton.disabled = false;
            this.submitButton.textContent = "Answer";
        }
    }

    private clearErrors(): void {
        this.form.querySelectorAll(".form__error-wrapper").forEach(wrapper => {
            wrapper.innerHTML = "";
        });
    }

    private displayErrors(errors: Record<string, string[]>): void {
        Object.keys(errors).forEach(fieldName => {
            const fieldElement = this.form.querySelector(`[name="${fieldName}"]`);

            if (fieldElement) {
                const fieldRow = fieldElement.closest(".form__row");
                const errorWrapper = fieldRow?.querySelector(".form__error-wrapper");

                if (fieldRow && errorWrapper) {
                    errors[fieldName].forEach(message => {
                        const errorHtml = `<span class="form__error-message">${message}</span>`;
                        errorWrapper.insertAdjacentHTML("beforeend", errorHtml);
                    });
                }
            }

            if (fieldName === "__all__") {
                const errorWrapper = this.form.querySelector(".form__error-wrapper--non-field");
                if (errorWrapper) {
                    errors[fieldName].forEach(message => {
                        const errorHtml = `<span class="form__error-message">${message}</span>`;
                        errorWrapper.insertAdjacentHTML("beforeend", errorHtml);
                    });
                }
            }
        })
    }

    static create = (): NewAnswerHandler | null => {
        const form = document.querySelector(".js-user-answer-form");
        const answersSection = document.querySelector(".js-answers-list");
        const answerContent = document.querySelector("[name=content]")
        const submitButton = document.querySelector(".js-submit-button")

        if (!(form instanceof HTMLFormElement) ||
            !(answersSection instanceof HTMLElement) ||
            !(answerContent instanceof HTMLTextAreaElement) ||
            !(submitButton instanceof HTMLButtonElement)) {
            console.error("Crucial elements required for NewAnswerHandler are missing or wrong type");
            return null;
        }

        return new NewAnswerHandler(
            form,
            answersSection,
            answerContent,
            submitButton
        )
    }
}


// TODO maybe refresh page on another tab logout
class ToggleVoteHandler {
    private CSRFToken: string = "";

    constructor() {
        this.readCSRFToken();
        document.body.addEventListener("click", this.handleClick)
    }

    private readCSRFToken = (): void => {
        if (document.cookie && document.cookie != "") {
            const cookies = Object.fromEntries(
                document.cookie.split("; ").map(value => value.split("="))
            );

            if ("csrftoken" in cookies) {
                this.CSRFToken = cookies.csrftoken;
            }
        }
    }

    private handleClick = (event: Event): void => {
        const target = event.target as HTMLElement
        const button = target.closest(".js-vote-button")

        if (button instanceof HTMLDivElement) {
            this.handleVote(button);
        }
    }

    private handleVote = async (voteButton: HTMLDivElement): Promise<void> => {
        const ratingInput = voteButton.closest(".js-rating-input") as HTMLDivElement;
        if (!ratingInput) {
            return;
        }

        const objectId = ratingInput.dataset.objectId;
        const objectType = ratingInput.dataset.objectType;
        const voteType = voteButton.dataset.voteType;

        const url = `/vote/${objectType}/${objectId}/${voteType}/`;

        try {
            const response = await fetch(url, {
                method: "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": this.CSRFToken,
                }
            });

            const result = await response.json()

            if (response.ok) {
                const ratingDisplay = ratingInput.querySelector(".js-rating-display");
                const likeButton = ratingInput.querySelector('[data-vote-type="1"]');
                const dislikeButton = ratingInput.querySelector('[data-vote-type="-1"]');

                if (ratingDisplay) {
                    ratingDisplay.textContent = result.new_rating;
                }

                likeButton.classList.remove("rating-input__button--active");
                dislikeButton.classList.remove("rating-input__button--active");

                if (result.vote_status == "liked") {
                    likeButton.classList.add("rating-input__button--active");
                } else if (result.vote_status == "disliked") {
                    dislikeButton.classList.add("rating-input__button--active");
                }
            } else {
                Toaster.makeToast([result.message], "error");
            }
        }

        catch (error) {
            console.error("Network or unexpected error:", error);
            Toaster.makeToast(["A network error occurred."], "error");
        }
    }
}


class MarkAnswerCorrectHandler {
    private CSRFToken: string = "";

    constructor() {
        this.readCSRFToken();
        document.body.addEventListener("click", this.handleClick)
    }

    private readCSRFToken = (): void => {
        if (document.cookie && document.cookie != "") {
            const cookies = Object.fromEntries(
                document.cookie.split("; ").map(value => value.split("=", 1))
            );

            if ("csrftoken" in cookies) {
                this.CSRFToken = cookies.csrftoken;
            }
        }
    }

    private handleClick = (event: Event): void => {
        const target = event.target as HTMLElement

        if (target instanceof HTMLButtonElement && target.matches(".js-mark-correct-button")) {
            this.handleMarkCorrect(target);
        }
    }

    private handleMarkCorrect = async (button: HTMLButtonElement): Promise<void> => {
        const questionId = button.dataset.questionId;
        const answerId = button.dataset.answerId;
        const questionCard = button.closest(".js-answer-card");

        const url = `/questions/${questionId}/${answerId}/mark-correct/`;

        try {
            const response = await fetch(url, {
                "method": "POST",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": this.CSRFToken,
                }
            });

            const result = await response.json();

            if (response.ok && questionCard) {
                questionCard.classList.add("answer--correct");
            }

            if (!response.ok) {
                Toaster.makeToast([result.message], "error");
            }
        }

        catch (error) {
            console.error("Network or unexpected error:", error);
            Toaster.makeToast(["A network error occurred."], "error");
        }
    }
}

class Toaster {
    private static body = document.body;

    static makeToast = (messages: string[], toastType: string = ""): void => {
        const toast = Object.assign(document.createElement("div"), {
            className: `toast ${toastType ? "toast--" + toastType : ""}`,
        });

        for (const message of messages) {
            toast.appendChild(Object.assign(document.createElement("div"), {
                className: "toast__message",
                textContent: message
            }))
        }
        this.body.appendChild(toast);

        setTimeout(() => this.removeToast(toast), 3000);
    }

    private static removeToast = (toast: HTMLDivElement): void => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }
}

document.addEventListener("DOMContentLoaded", checkActiveTab);
document.addEventListener("DOMContentLoaded", initTheme);
document.addEventListener("DOMContentLoaded", checkDjangoMessages)
CustomFileInput.create()
NewAnswerHandler.create()
new ToggleVoteHandler;
new MarkAnswerCorrectHandler;
