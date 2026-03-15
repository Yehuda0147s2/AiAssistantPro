import Dexie from 'dexie';

export class Store {
    constructor(app) {
        this.app = app;
        this.db = new Dexie('ImpervoDB');
    }

    async init() {
        this.db.version(1).stores({
            settings: 'key, value'
        });
        await this.db.open();
    }

    async getSetting(key, defaultValue = null) {
        const item = await this.db.settings.get(key);
        return item ? item.value : defaultValue;
    }

    async setSetting(key, value) {
        await this.db.settings.put({ key, value });
    }
}
