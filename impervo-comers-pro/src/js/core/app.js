import { Router } from './router.js';
import { Store } from './store.js';
import { Theme } from './theme.js';
import { I18n } from './i18n.js';
import { Events } from './events.js';

export class App {
    constructor() {
        this.events = new Events();
        this.store = new Store(this);
        this.theme = new Theme(this);
        this.i18n = new I18n(this);
        this.router = new Router(this);
        this.modules = {};
    }

    async init() {
        console.log('Impervo Comers Pro initializing...');
        await this.store.init();
        await this.i18n.init();
        await this.theme.init();
        this.router.init();
        this.setupGlobalEvents();
        console.log('App ready');
    }

    setupGlobalEvents() {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const nav = e.currentTarget.getAttribute('data-nav');
                if (nav) {
                    this.router.navigate(nav);
                }
            });
        });

        document.getElementById('theme-toggle').onclick = () => {
            const next = this.theme.currentTheme === 'light' ? 'dark' : 'light';
            this.theme.applyTheme(next);
            this.theme.currentTheme = next;
        };
    }

    updateActiveNav(nav) {
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.getAttribute('data-nav') === nav);
        });
    }
}
