import { Scanner } from './scanner.js';

export default class DeviceScanner {
    constructor(app) {
        this.app = app;
        this.scanner = new Scanner(app);
    }

    async render(container) {
        container.innerHTML = `
            <div class="scanner-module fade-in">
                <div class="card" style="text-align:center; padding:40px;">
                    <div style="width:120px; height:120px; border-radius:60px; border:8px solid var(--primary); margin:0 auto 20px; display:flex; align-items:center; justify-content:center; font-size:24px; font-weight:700;">
                        98%
                    </div>
                    <h2>System Health</h2>
                    <p>Your device is optimized and secure.</p>
                    <button id="scan-btn" class="btn btn-primary btn-round" style="margin-top:24px;">Scan Now</button>
                </div>
            </div>
        `;
    }
}
