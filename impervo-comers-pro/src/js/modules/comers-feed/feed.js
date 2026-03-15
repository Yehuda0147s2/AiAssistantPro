export class Feed {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="card">
                <div style="display:flex; align-items:center; margin-bottom:12px;">
                    <div style="width:40px; height:40px; border-radius:20px; background:var(--bg-tertiary); margin-right:12px;"></div>
                    <div>
                        <div style="font-weight:600;">Samsung News</div>
                        <div style="font-size:12px; color:var(--text-tertiary);">2h ago</div>
                    </div>
                </div>
                <p>Check out the new Galaxy features integrated into Impervo Comers Pro!</p>
            </div>
        `;
    }
}
