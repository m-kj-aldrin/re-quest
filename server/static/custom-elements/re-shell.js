class ReShell extends HTMLElement {
    constructor() {
        super();

        this.addEventListener("submit", async (e) => {
            if (!(e.target instanceof HTMLFormElement)) return;
            e.preventDefault();

            let form = e.target;
            let formData = new FormData(form);
            let method = form.getAttribute("method") ?? form.method;
            let action = form.action;

            let response = await this.#fetch({
                path: action,
                method,
                body: formData,
            });

            if (response.ok) {
                let responseString = await response.text();
                let extracted = this.#extractFragments(responseString);
                let fragments = extracted.map(this.makeFragment.bind(this));

                this.reTarget(fragments);

                if (this.hasAttribute("clear-form")) {
                    form.reset();
                }
            }
        });

        this.addEventListener(
            "re-action",
            /**@param {ReActionEvent} e*/
            async (e) => {
                this.reTarget(e.data.docs);
            }
        );
    }

    /**
     * @typedef {Object} TargetContent
     * @prop {string} target
     * @prop {string} content
     */

    /**
     * @param {string} partial
     * @returns {TargetContent[]}
     */
    #extractFragments(partial) {
        const result = [];
        const reFragmentRegex =
            /<re-fragment target="([^"]+)">(.*?)<\/re-fragment>/gs;
        let match;
        while ((match = reFragmentRegex.exec(partial)) !== null) {
            const target = match[1];
            const content = match[2].trim();
            result.push({ target, content });
            partial = partial.replace(match[0], "");
        }

        const targetElementRegex =
            /<([a-zA-Z0-9-]+)[^>]*target="([^"]+)"[^>]*>(.*?)<\/\1>/gs;
        while ((match = targetElementRegex.exec(partial)) !== null) {
            const tag = match[1];
            const target = match[2];
            const outerHtml = match[0];
            result.push({ target, content: outerHtml });
        }

        return result;
    }

    /**
     * @param {TargetContent} o
     */
    makeFragment(o) {
        const frag = document.createDocumentFragment();
        frag.title = o.target;
        let parsed = this.#parseHTML(o.content);

        frag.replaceChildren(...parsed.children);

        return frag;
    }

    #parseHTML(str) {
        let parser = (s) => new DOMParser().parseFromString(s, "text/html");
        const doc = parser(
            "<body><template>" + str + "</template></body>"
        ).querySelector("template").content;
        return doc;
    }

    /**
     * @param {Object} o
     * @param {string} o.path
     * @param {string} o.method
     * @param {BodyInit} o.body
     */
    #fetch({ path, method, body }) {
        let response = fetch(path, {
            method,
            body,
        });

        return response;
    }

    /**
     * @param {DocumentFragment[]} fragments
     */
    reTarget(fragments) {
        fragments.forEach((fragment) => {
            let targetName = fragment.title;
            let target = this.querySelector(`re-target[name="${targetName}"]`);
            if (target.hasAttribute("selector")) {
                target = target.querySelector(target.getAttribute("selector"));
            }

            target.replaceChildren(...fragment.children);
        });
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-shell", ReShell);
