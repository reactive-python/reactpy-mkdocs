import { mount, SimpleReactPyClient } from "@reactpy/client";

// DO NOT EDIT: this is substituted when running the mkdocs dev server
const BASE_URL = document.location.origin;

class ReactPyFrame extends HTMLElement {
  connectedCallback() {
    // check that reactpy-frame has a file attribute
    if (!this.hasAttribute("file")) {
      throw new Error("reactpy-frame must have a file attribute");
    }

    // url encode the filename
    const filename = encodeURIComponent(this.getAttribute("file"));

    const client = new SimpleReactPyClient({
      serverLocation: {
        url: BASE_URL,
        route: document.location.pathname,
        query: `?file=${filename}`,
      },
    });
    mount(this, client);
  }
}

customElements.define("reactpy-frame", ReactPyFrame);
