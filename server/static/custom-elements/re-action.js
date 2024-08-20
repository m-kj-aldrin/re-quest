class ReActionEvent extends Event {
    #data;

    /**
     * @param {Object} data
     * @param {Document} data.doc
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

    async action() {
        let href = this.getAttribute("href") ?? "";
        let method = this.getAttribute("method") ?? "get";
        let data = method == "get" ? undefined : this.#getData();

        let response = await this.#fetch({ href, method, body: data });

        if (response.ok) {
            let responseString = await response.text();
            let doc = new DOMParser().parseFromString(
                responseString,
                "text/html"
            );

            this.#send(doc);
        }
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

        // Log the formatted JSON string for debugging
        console.log("Formatted JSON String:", jsonString);

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
     * @param {Document} doc
     */
    #send(doc) {
        this.dispatchEvent(new ReActionEvent({ doc }));
    }

    /**
     * @param {Object} o
     * @param {string} o.href
     * @param {string} o.method
     * @param {BodyInit} o.body
     */
    #fetch({ href, method, body }) {
        let headers = new Headers();
        if (body) {
            headers.append("Content-Type", "application/json");
        }
        let response = fetch(href, {
            method,
            body,
        });

        return response;
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-action", ReAction);
