export class Theme {
    constructor(app) {
        this.app = app;
    }

    async init() {
        this.currentTheme = await this.app.store.getSetting('theme', 'light');
        this.applyTheme(this.currentTheme);
    }

    applyTheme(theme) {
        document.body.className = `theme-${theme}`;
    }
}
