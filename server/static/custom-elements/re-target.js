class ReTarget extends HTMLElement {
    constructor() {
        super();

        this.addEventListener(
            "re-action",
            /**@param {ReActionEvent} e */
            (e) => {
                this.#reTarget(e.data.doc);
            }
        );
    }

    /**
     * @param {Document} doc
     */
    #reTarget(doc) {
        this.replaceChildren(...doc.body.children);
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-target", ReTarget);
