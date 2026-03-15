export class Stories {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = '<div style="display:flex; overflow-x:auto;">Stories Placeholder</div>';
    }
}
