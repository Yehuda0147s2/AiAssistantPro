export class Comments {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = '<div>No comments yet.</div>';
    }
}
