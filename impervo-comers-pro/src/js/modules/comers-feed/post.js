export class Post {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="card">
                <textarea class="btn btn-secondary btn-block" style="text-align:left; min-height:60px; border:none;" placeholder="What's happening?"></textarea>
                <div style="display:flex; justify-content:flex-end; margin-top:12px;">
                    <button class="btn btn-primary btn-round">Post</button>
                </div>
            </div>
        `;
    }
}
