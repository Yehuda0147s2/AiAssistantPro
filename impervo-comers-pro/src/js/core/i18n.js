export class I18n {
    constructor(app) {
        this.app = app;
    }

    async init() {
        this.locale = await this.app.store.getSetting('language', 'en');
    }

    t(key) {
        return key;
    }
}
