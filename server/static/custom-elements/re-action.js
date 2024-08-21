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

            // this.reTarget(fragments);

            // if (this.hasAttribute("clear-form")) {
            //     form.reset();
            // }
        }

        // if (response.ok) {
        //     let responseString = await response.text();
        //     // let doc = new DOMParser().parseFromString(
        //     //     responseString,
        //     //     "text/html"
        //     // );

        //     this.#send(doc);
        // }
    }

    convertToJson(jsObjectString) {
        // Step 1: Add double quotes around keys (anything that looks like a key)
        let jsonString = jsObjectString.replace(
            /([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:)/g,
            '$1"$2"$3'
        );

        // Step 2: Ensure strings are properly quoted
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

    // /**
    //  * @param {Object} o
    //  * @param {string} o.href
    //  * @param {string} o.method
    //  * @param {BodyInit} o.body
    //  */
    // #fetch({ href, method, body }) {
    //     let headers = new Headers();
    //     if (body) {
    //         headers.append("Content-Type", "application/json");
    //     }
    //     let response = fetch(href, {
    //         method,
    //         body,
    //     });

    //     return response;
    // }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-action", ReAction);
