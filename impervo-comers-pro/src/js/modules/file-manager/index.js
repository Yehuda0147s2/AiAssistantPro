import { Explorer } from './explorer.js';
import { Storage } from './storage.js';

export default class FileManager {
    constructor(app) {
        this.app = app;
        this.explorer = new Explorer(app);
        this.storage = new Storage(app);
    }

    async render(container) {
        container.innerHTML = `
            <div class="file-manager-container fade-in">
                <div class="storage-summary card">
                    <h3>Storage Analysis</h3>
                    <div id="storage-stats"></div>
                </div>
                <div class="explorer-toolbar" style="display:flex; justify-content:space-between; margin-bottom:16px;">
                    <input type="text" id="file-search" placeholder="Search files..." class="btn btn-secondary" style="flex:1; margin-right:8px;">
                    <button id="add-file" class="btn btn-primary">Add File</button>
                </div>
                <div id="file-explorer-root"></div>
            </div>
        `;
        await this.explorer.render(document.getElementById('file-explorer-root'));
        await this.storage.render(document.getElementById('storage-stats'));
    }
}
