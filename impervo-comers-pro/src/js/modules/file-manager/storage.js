export class Storage {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div style="margin-top:10px;">
                <div style="height:8px; background:var(--bg-tertiary); border-radius:4px; overflow:hidden;">
                    <div style="width:45%; height:100%; background:var(--primary);"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-size:12px; margin-top:4px;">
                    <span>54.2 GB used</span>
                    <span>128 GB total</span>
                </div>
            </div>
        `;
    }
}
