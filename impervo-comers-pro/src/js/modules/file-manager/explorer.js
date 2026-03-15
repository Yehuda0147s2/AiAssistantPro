export class Explorer {
    constructor(app) {
        this.app = app;
        this.files = [
            { id: 1, name: 'Documents', type: 'folder', size: 0, date: new Date() },
            { id: 2, name: 'Images', type: 'folder', size: 0, date: new Date() },
            { id: 3, name: 'presentation.pptx', type: 'file', size: 15400000, date: new Date() },
            { id: 4, name: 'budget.xlsx', type: 'file', size: 250000, date: new Date() }
        ];
    }

    async render(container) {
        this.container = container;
        this.refresh();
    }

    refresh() {
        this.container.innerHTML = `
            <div class="file-grid">
                ${this.files.map(file => `
                    <div class="file-item card" style="display:flex; flex-direction:column; align-items:center;">
                        <span style="font-size:32px;">${file.type === 'folder' ? '📁' : '📄'}</span>
                        <span style="margin-top:8px; font-size:12px; text-align:center;">${file.name}</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
}
