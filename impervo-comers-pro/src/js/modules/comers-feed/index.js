import { Feed } from './feed.js';
import { Post } from './post.js';

export default class ComersFeed {
    constructor(app) {
        this.app = app;
        this.feed = new Feed(app);
        this.postCreator = new Post(app);
    }

    async render(container) {
        container.innerHTML = `
            <div class="feed-module fade-in">
                <div id="post-creator-root" style="margin-bottom:20px;"></div>
                <div id="feed-root"></div>
            </div>
        `;
        await this.postCreator.render(document.getElementById('post-creator-root'));
        await this.feed.render(document.getElementById('feed-root'));
    }
}
