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
                // let doc = new DOMParser().parseFromString(
                //     `<body><template>${responseString}</template></body>`,
                //     "text/html"
                // ).querySelector("template");
                // let template = document.createElement("template");
                // template.innerHTML = responseString;
                // let doc = template.content;
                let strippedText = this.#extractReFragment(responseString);
                console.log(strippedText);

                let doc = this.#parseHTML(strippedText.content);

                // console.log(doc.querySelector("re-fragment"));

                // console.log(doc.querySelector("tr"));

                // console.log(doc);

                this.reTarget(doc);

                if (this.hasAttribute("clear-form")) {
                    form.reset();
                }
            }
        });

        this.addEventListener(
            "re-action",
            /**@param {ReActionEvent} e*/
            async (e) => {
                this.reTarget(e.data.doc);
            }
        );
    }

    #stripResponse(str) {}

    #extractReFragment(htmlString) {
        // Define a regex to match the <re-fragment> element and capture the target attribute
        const reFragmentRegex =
            /<re-fragment\s+target="([^"]+)"\s*>([\s\S]*?)<\/re-fragment>/gi;

        let target = null;
        let contentWithoutReFragment = htmlString;

        // Use the regex to find and replace the <re-fragment> elements
        contentWithoutReFragment = contentWithoutReFragment.replace(
            reFragmentRegex,
            function (match, targetAttr, innerContent) {
                // Extract the target attribute value
                target = targetAttr;

                // Return the inner content without the <re-fragment> wrapper
                return innerContent.trim();
            }
        );

        return {
            target: target, // Extracted target attribute value
            content: contentWithoutReFragment, // HTML content without <re-fragment>
        };
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
     * @param {DocumentFragment} doc
     */
    reTarget(doc) {
        console.log(doc.querySelector("tr"));

        let reTargetableElements = doc.querySelectorAll("[target]");
        console.log(reTargetableElements);

        reTargetableElements.forEach((element) => {
            let targetName = element.getAttribute("target");
            let target = this.querySelector(`re-target[name="${targetName}"]`);
            if (target.hasAttribute("selector")) {
                target = target.querySelector(target.getAttribute("selector"));
                // console.log(target);
            }

            let shouldConsume = target.hasAttribute("consume");

            if (element.tagName.toLowerCase() == "re-fragment") {
                let children = element.children;

                console.log(element);

                console.log(children);

                if (shouldConsume) {
                    // target.replaceChildren(element);
                } else {
                    // target.replaceChildren(...children);
                }
            }

            if (shouldConsume) {
                // target.replaceChildren(element);
            } else {
                // target.replaceChildren(element.cloneNode(true));
            }
        });
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-shell", ReShell);
