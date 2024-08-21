class ReTarget extends HTMLElement {
    constructor() {
        super();

        this.addEventListener(
            "re-action",
            /**@param {ReActionEvent} e */
            (e) => {
                if (!this.hasAttribute("name")) return;
                this.#reTarget(e.data.docs);
            }
        );
    }

    /**
     * @param {DocumentFragment[]} docs
     */
    #reTarget(docs) {
        // this.replaceChildren(...docs.children);
        // docs.forEach(fragment =>{
        // })
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-target", ReTarget);
