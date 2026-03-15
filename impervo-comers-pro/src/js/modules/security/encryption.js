import CryptoJS from 'crypto-js';

export class Encryption {
    constructor(app) {
        this.app = app;
    }

    encrypt(data, key) {
        return CryptoJS.AES.encrypt(JSON.stringify(data), key).toString();
    }

    decrypt(ciphertext, key) {
        const bytes = CryptoJS.AES.decrypt(ciphertext, key);
        return JSON.parse(bytes.toString(CryptoJS.enc.Utf8));
    }
}
