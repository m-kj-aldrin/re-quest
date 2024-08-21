class ReActionEvent extends Event {
    #data;

    /**
     * @param {Object} data
     * @param {DocumentFragment[]} data.docs
     */
    constructor(data) {
        super("re-action", { bubbles: true });
        this.#data = data;
    }

    get data() {
        return this.#data;
    }
}

class ReAction extends HTMLElement {
    constructor() {
        super();

        this.addEventListener("click", this.action);
    }

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
    async action() {
        let href = this.getAttribute("href") ?? "";
        let method = this.getAttribute("method") ?? "get";
        let data = method == "get" ? undefined : this.#getData();

        let response = await this.#fetch({ path: href, method, body: data });

        if (response.ok) {
            let responseString = await response.text();
            let extracted = this.#extractFragments(responseString);
            let fragments = extracted.map(this.makeFragment.bind(this));

            this.#send(fragments);
        }
    }

    convertToJson(jsObjectString) {
        let jsonString = jsObjectString.replace(
            /([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)/g,
            '$1"$2"$3'
        );

        jsonString = jsonString.replace(
            /:\s*([a-zA-Z_][a-zA-Z0-9_]*)/g,
            (match, p1) => {
                if (!["true", "false", "null"].includes(p1)) {
                    return `: "${p1}"`;
                }
                return match;
            }
        );

        return jsonString;
    }

    #getData() {
        let dataAttr = this.getAttribute("data");
        try {
            return this.convertToJson(dataAttr);
        } catch (error) {
            return {};
        }
    }

    /**
     * @param {DocumentFragment[]} docs
     */
    #send(docs) {
        this.dispatchEvent(new ReActionEvent({ docs }));
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-action", ReAction);

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

            console.log("request");

            let response = await this.#fetch({
                path: action,
                method,
                body: formData,
            });

            console.log("response");

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
    #reTarget(docs) {}

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-target", ReTarget);

window.addEventListener("DOMContentLoaded", (_) => {
    document
        .querySelectorAll("re-fragment")
        .forEach((element) => element.remove());
    let style = new CSSStyleSheet();
    style.replaceSync(`:where(re-shell, re-target) {
        display: contents;
    }`);
    document.adoptedStyleSheets.push(style);
});

// let xmlDoc = /**@type {XMLDocument} */ (
//     new DOMParser().parseFromString("<root></root>", "application/xml")
// );

// /**
//  *
//  * @param {string} tag
//  * @returns {Element}
//  */
// function createElement(tag) {
//     return xmlDoc.createElement(tag);
// }

// /**
//  * @param {string} name
//  * @param {string} value
//  */
// function createItem(name, value) {
//     let item = createElement("item");
//     let nameEl = createElement("name");
//     nameEl.textContent = name;
//     let valueEl = createElement("value");
//     valueEl.textContent = value;

//     item.append(nameEl, valueEl);

//     return item;
// }
