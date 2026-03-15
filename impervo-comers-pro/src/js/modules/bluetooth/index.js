export default class BluetoothModule {
    constructor(app) {
        this.app = app;
    }

    async render(container) {
        container.innerHTML = `
            <div class="bluetooth-module fade-in">
                <div class="card" style="text-align:center;">
                    <div style="font-size:48px; margin-bottom:16px;">📶</div>
                    <h2>Bluetooth Share</h2>
                    <p>Discover nearby devices to share files securely.</p>
                    <button class="btn btn-primary btn-block" style="margin-top:20px;">Search Devices</button>
                </div>
            </div>
        `;
    }
}
