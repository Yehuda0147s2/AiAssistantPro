import { Encryption } from '../../src/js/modules/security/encryption.js';

describe('Encryption Module', () => {
    let encryption;
    const mockApp = {};

    beforeEach(() => {
        encryption = new Encryption(mockApp);
    });

    test('should encrypt and decrypt data correctly', () => {
        const data = { message: 'secret' };
        const key = 'secret-key';
        const encrypted = encryption.encrypt(data, key);
        const decrypted = encryption.decrypt(encrypted, key);
        expect(decrypted).toEqual(data);
    });
});
