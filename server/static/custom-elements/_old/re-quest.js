class ReQuest extends HTMLElement {
    constructor() {
        super();

        let parser = new DOMParser();

        this.addEventListener("submit", async (e) => {
            let body = new FormData();
            let method;
            let action;

            if (e.target instanceof HTMLFormElement) {
                let form = e.target;
                method =
                    form.getAttribute("method").toLowerCase() ?? form.method;

                if (e.submitter.hasAttribute("method")) {
                    method = e.submitter.getAttribute("method");
                }

                body = new FormData(form);
                action = form.action;

                e.preventDefault();
            } else if (e.target instanceof HTMLElement) {
                if (e.target.hasAttribute("method")) {
                    e.preventDefault();
                    method = e.target.getAttribute("method");
                    action = e.target.getAttribute("action") ?? "";
                }
            }

            let response = await fetch(action, {
                method,
                body,
            });

            if (response.ok) {
                let responseText = await response.text();

                let responseDom = parser.parseFromString(
                    responseText,
                    "text/html"
                );

                Array.from(responseDom.querySelectorAll("[target]")).map(
                    (element) => {
                        let targetElement = this.querySelector(
                            `re-target[name="${element.getAttribute(
                                "target"
                            )}"]`
                        );

                        targetElement.replaceChildren(element);
                    }
                );
            }
        });
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-quest", ReQuest);
