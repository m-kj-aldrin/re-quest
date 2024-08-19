class ReTrigger extends HTMLElement {
    constructor() {
        super();

        let [command, ...parameters] = this.getAttribute("on").split(" ");

        switch (command) {
            case "load":
                this.dispatch();
                break;
            case "delay":
                setTimeout(() => {
                    this.dispatch();
                }, +parameters[0]);
                break;
            case "repeat":
                let id = setInterval(() => {
                    this.dispatch();
                }, +parameters[0]);

                this.addEventListener("reset", (_) => clearInterval(id));
        }
    }

    dispatch() {
        this.dispatchEvent(new CustomEvent("trigger", { bubbles: true }));
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("re-trigger", ReTrigger);
