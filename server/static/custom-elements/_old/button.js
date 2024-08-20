/**
 * @param {string} dataString
 */
function parseDataAttribute(dataString) {
    if (!(typeof dataString == "string")) return {};
    let data = [];
    let items = dataString.split(",");
    items.forEach((item) => {
        let [key, value] = item.split(":");
        if (value) {
            data.push({ [key]: value });
        } else {
            data.push({ value: key });
        }
    });
    return data;
}

class Button extends HTMLElement {
    constructor() {
        super();

        this.addEventListener("click", (_) => {
            let name = this.getAttribute("data-message");
            let data = this.getAttribute("data-data");

            data = parseDataAttribute(data);

            this.dispatchEvent(
                new CustomEvent(name, { bubbles: true, detail: data })
            );
        });
    }

    connectedCallback() {}
    disconnectedCallback() {}
}

customElements.define("x-button", Button);
