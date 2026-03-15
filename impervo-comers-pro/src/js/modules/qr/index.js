import QRCode from 'qrcode';

export default class QRModule {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="qr-module fade-in">
                <div class="card" style="text-align:center;">
                    <canvas id="qr-canvas" style="width:200px; height:200px; margin:0 auto;"></canvas>
                    <p style="margin-top:16px;">Scan to share your profile</p>
                    <button class="btn btn-primary btn-block" style="margin-top:20px;">Generate New</button>
                </div>
            </div>
        `;
        QRCode.toCanvas(document.getElementById('qr-canvas'), 'impervo-user-123', { width: 200 });
    }
}
