export default class AnalyticsModule {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="analytics-module card fade-in">
                <h3>Sharing Insights</h3>
                <div style="margin-top:20px;">
                    <div style="font-size:24px; font-weight:700;">1.2 GB</div>
                    <div style="font-size:12px; color:var(--text-tertiary);">Shared this week</div>
                </div>
            </div>
        `;
    }
}
