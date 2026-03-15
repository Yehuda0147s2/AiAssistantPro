export default class CloudModule {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="cloud-module fade-in">
                <div class="card">
                    <h3>Connected Clouds</h3>
                    <div style="margin-top:12px;">
                        <div class="btn btn-secondary btn-block" style="justify-content:flex-start; margin-bottom:8px;">☁️ Samsung Cloud</div>
                        <div class="btn btn-secondary btn-block" style="justify-content:flex-start;">📂 Google Drive</div>
                    </div>
                </div>
            </div>
        `;
    }
}
