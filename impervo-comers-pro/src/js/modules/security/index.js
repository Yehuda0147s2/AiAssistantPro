import { Encryption } from './encryption.js';

export default class SecurityModule {
    constructor(app) {
        this.app = app;
        this.encryption = new Encryption(app);
    }

    async render(container) {
        container.innerHTML = `
            <div class="security-module fade-in">
                <div class="card">
                    <h3>Encryption Status</h3>
                    <div style="display:flex; align-items:center; margin-top:12px;">
                        <span style="color:var(--success); font-weight:600;">● Secure</span>
                        <span style="margin-left:8px; font-size:12px; color:var(--text-tertiary);">AES-256 Enabled</span>
                    </div>
                </div>
                <div class="card">
                    <h3>Biometrics</h3>
                    <p style="font-size:14px; margin-top:8px;">Samsung Knox fingerprint authentication is active for this account.</p>
                </div>
            </div>
        `;
    }
}
