export class Router {
    constructor(app) {
        this.app = app;
        this.routes = {
            'feed': 'comers-feed',
            'file-manager': 'file-manager',
            'device-scanner': 'device-scanner',
            'sharing': 'bluetooth',
            'settings': 'analytics' // fallback
        };
    }

    init() {
        window.addEventListener('hashchange', () => this.handleRoute());
        this.handleRoute();
    }

    async handleRoute() {
        const hash = window.location.hash.slice(1) || 'feed';
        const moduleName = this.routes[hash];
        if (moduleName) {
            await this.loadModule(moduleName);
            this.app.updateActiveNav(hash);
        }
    }

    navigate(path) {
        window.location.hash = path;
    }

    async loadModule(moduleName) {
        const contentArea = document.getElementById('main-content');
        contentArea.innerHTML = '<div class="shimmer-container"><div class="shimmer-card"></div></div>';
        try {
            const module = await import(`../modules/${moduleName}/index.js`);
            const instance = new module.default(this.app);
            await instance.render(contentArea);
            document.getElementById('page-title').innerText = moduleName.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ');
        } catch (e) {
            console.error(e);
            contentArea.innerHTML = 'Error loading module';
        }
    }
}
