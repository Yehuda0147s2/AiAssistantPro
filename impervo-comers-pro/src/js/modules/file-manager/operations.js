export class Operations {
    constructor(app) {
        this.app = app;
    }

    async delete(file) {
        console.log('Deleting:', file);
    }
}
