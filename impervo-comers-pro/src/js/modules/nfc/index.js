export default class NFCModule {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="nfc-module card fade-in" style="text-align:center;">
                <div style="font-size:48px;">📳</div>
                <h3>NFC One-Tap</h3>
                <p>Bring devices together to share instantly.</p>
            </div>
        `;
    }
}
