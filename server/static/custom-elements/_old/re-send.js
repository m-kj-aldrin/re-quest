class ReSend extends HTMLElement {
    constructor() {
        super();

        this.addEventListener("click", (_) => this.send());
        this.addEventListener("trigger", (e) => {
            e.stopPropagation();
            this.send();
        });
    }

    send() {
        let event = new SubmitEvent("submit", {
            bubbles: true,
            submitter: this,
        });

        let parentForm = this.closest("re-quest form");
        if (parentForm instanceof HTMLFormElement) {
            parentForm.dispatchEvent(event);
        } else {
            this.dispatchEvent(event);
        }
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-send", ReSend);
