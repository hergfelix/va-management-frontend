#!/usr/bin/env node
/**
 * Agent 5: Puppeteer with Stealth Plugin
 * Node.js TikTok scraper with advanced anti-detection measures
 */

const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const { executablePath } = require('puppeteer');

// Add stealth plugin
puppeteer.use(StealthPlugin());

class PuppeteerTikTokScraper {
    constructor(options = {}) {
        this.headless = options.headless !== false;
        this.timeout = options.timeout || 30000;
        this.delay = options.delay || 2000;
        this.costPerPost = 0.00015; // Slightly higher than Playwright
        this.browser = null;
    }

    async init() {
        /**
         * Initialize browser with stealth configuration
         */
        this.browser = await puppeteer.launch({
            headless: this.headless,
            executablePath: executablePath(),
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-blink-features=AutomationControlled',
                '--disable-features=VizDisplayCompositor'
            ],
            ignoreDefaultArgs: ['--enable-automation'],
            ignoreHTTPSErrors: true
        });
    }

    async close() {
        /**
         * Close browser instance
         */
        if (this.browser) {
            await this.browser.close();
        }
    }

    async scrapePostMetrics(postUrl) {
        /**
         * Scrape metrics for a single TikTok post
         */
        const page = await this.browser.newPage();
        
        try {
            // Set realistic viewport
            await page.setViewport({
                width: 1920,
                height: 1080,
                deviceScaleFactor: 1
            });

            // Set realistic user agent
            await page.setUserAgent(
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
                '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            );

            // Set extra headers
            await page.setExtraHTTPHeaders({
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0'
            });

            // Navigate to post
            console.log(`Scraping: ${postUrl}`);
            await page.goto(postUrl, {
                waitUntil: 'networkidle2',
                timeout: this.timeout
            });

            // Wait for content to load
            await page.waitForTimeout(this.delay);

            // Extract metrics
            const metrics = await this.extractMetrics(page, postUrl);
            
            console.log(`Successfully scraped: ${postUrl}`);
            return metrics;

        } catch (error) {
            console.error(`Failed to scrape ${postUrl}:`, error.message);
            return {
                post_url: postUrl,
                error: error.message,
                scraped_at: Date.now()
            };
        } finally {
            await page.close();
        }
    }

    async extractMetrics(page, postUrl) {
        /**
         * Extract metrics from TikTok page
         */
        const metrics = {
            post_url: postUrl,
            scraped_at: Date.now()
        };

        try {
            // Wait for metrics to load
            await page.waitForSelector('[data-e2e="video-views"]', { timeout: 10000 });

            // Extract views
            try {
                const viewsElement = await page.$('[data-e2e="video-views"]');
                if (viewsElement) {
                    const viewsText = await page.evaluate(el => el.textContent, viewsElement);
                    metrics.views = this.parseMetric(viewsText);
                }
            } catch (e) {
                metrics.views = 0;
            }

            // Extract likes
            try {
                const likesElement = await page.$('[data-e2e="like-count"]');
                if (likesElement) {
                    const likesText = await page.evaluate(el => el.textContent, likesElement);
                    metrics.likes = this.parseMetric(likesText);
                }
            } catch (e) {
                metrics.likes = 0;
            }

            // Extract comments
            try {
                const commentsElement = await page.$('[data-e2e="comment-count"]');
                if (commentsElement) {
                    const commentsText = await page.evaluate(el => el.textContent, commentsElement);
                    metrics.comments = this.parseMetric(commentsText);
                }
            } catch (e) {
                metrics.comments = 0;
            }

            // Extract shares
            try {
                const sharesElement = await page.$('[data-e2e="share-count"]');
                if (sharesElement) {
                    const sharesText = await page.evaluate(el => el.textContent, sharesElement);
                    metrics.shares = this.parseMetric(sharesText);
                }
            } catch (e) {
                metrics.shares = 0;
            }

            // Extract bookmarks
            try {
                const bookmarksElement = await page.$('[data-e2e="bookmark-count"]');
                if (bookmarksElement) {
                    const bookmarksText = await page.evaluate(el => el.textContent, bookmarksElement);
                    metrics.bookmarks = this.parseMetric(bookmarksText);
                }
            } catch (e) {
                metrics.bookmarks = 0;
            }

            // Calculate engagement rate
            if (metrics.views > 0) {
                const totalEngagement = metrics.likes + metrics.comments + metrics.shares + metrics.bookmarks;
                metrics.engagement_rate = Math.round((totalEngagement / metrics.views) * 100 * 100) / 100;
            } else {
                metrics.engagement_rate = 0.0;
            }

        } catch (error) {
            console.warn(`Error extracting metrics: ${error.message}`);
            // Set default values
            Object.assign(metrics, {
                views: 0,
                likes: 0,
                comments: 0,
                shares: 0,
                bookmarks: 0,
                engagement_rate: 0.0
            });
        }

        return metrics;
    }

    parseMetric(value) {
        /**
         * Parse TikTok metric format (e.g., '10.5K' -> 10500)
         */
        if (!value) return 0;

        const cleanValue = value.toString().toUpperCase().replace(/[^\d.KMB]/g, '');

        if (cleanValue.includes('K')) {
            return Math.floor(parseFloat(cleanValue.replace('K', '')) * 1000);
        } else if (cleanValue.includes('M')) {
            return Math.floor(parseFloat(cleanValue.replace('M', '')) * 1000000);
        } else if (cleanValue.includes('B')) {
            return Math.floor(parseFloat(cleanValue.replace('B', '')) * 1000000000);
        } else {
            return parseInt(cleanValue) || 0;
        }
    }

    async scrapeBatch(postUrls, delay = 2000) {
        /**
         * Scrape multiple posts with rate limiting
         */
        const results = [];

        for (let i = 0; i < postUrls.length; i++) {
            const url = postUrls[i];
            
            try {
                const result = await this.scrapePostMetrics(url);
                results.push(result);

                // Rate limiting
                if (i < postUrls.length - 1) {
                    await new Promise(resolve => setTimeout(resolve, delay));
                }

            } catch (error) {
                console.error(`Batch scraping error for ${url}:`, error.message);
                results.push({
                    post_url: url,
                    error: error.message,
                    scraped_at: Date.now()
                });
            }
        }

        return results;
    }

    async scrapeBatchParallel(postUrls, maxConcurrent = 3, delay = 1000) {
        /**
         * Scrape multiple posts in parallel with concurrency control
         */
        const results = [];
        const semaphore = new Array(maxConcurrent).fill(null);
        let index = 0;

        const worker = async () => {
            while (index < postUrls.length) {
                const currentIndex = index++;
                const url = postUrls[currentIndex];

                try {
                    const result = await this.scrapePostMetrics(url);
                    results[currentIndex] = result;

                    // Rate limiting
                    await new Promise(resolve => setTimeout(resolve, delay));

                } catch (error) {
                    console.error(`Parallel scraping error for ${url}:`, error.message);
                    results[currentIndex] = {
                        post_url: url,
                        error: error.message,
                        scraped_at: Date.now()
                    };
                }
            }
        };

        // Start workers
        await Promise.all(semaphore.map(() => worker()));

        return results;
    }
}

// Test function
async function testPuppeteerScraper() {
    const testUrls = [
        'https://www.tiktok.com/@miriamrollqueen/video/7502407048114605354',
        'https://www.tiktok.com/@miriglow/video/7502422163824151851',
        // Add more test URLs here
    ];

    const scraper = new PuppeteerTikTokScraper({
        headless: true,
        timeout: 30000,
        delay: 3000
    });

    try {
        await scraper.init();
        console.log('Testing Puppeteer TikTok Scraper...');

        const startTime = Date.now();
        const results = await scraper.scrapeBatch(testUrls, 2000);
        const endTime = Date.now();

        // Calculate metrics
        const successfulScrapes = results.filter(r => !r.error);
        const successRate = (successfulScrapes.length / testUrls.length) * 100;
        const totalTime = (endTime - startTime) / 1000;
        const postsPerMinute = (testUrls.length / totalTime) * 60;

        console.log('\n=== Puppeteer Scraper Test Results ===');
        console.log(`Posts tested: ${testUrls.length}`);
        console.log(`Success rate: ${successRate.toFixed(1)}%`);
        console.log(`Total time: ${totalTime.toFixed(2)} seconds`);
        console.log(`Speed: ${postsPerMinute.toFixed(1)} posts/minute`);
        console.log(`Cost: $${(testUrls.length * scraper.costPerPost).toFixed(4)}`);

        // Show sample results
        results.slice(0, 2).forEach(result => {
            if (!result.error) {
                console.log('\nSample result:');
                console.log(`  URL: ${result.post_url}`);
                console.log(`  Views: ${result.views?.toLocaleString() || 0}`);
                console.log(`  Likes: ${result.likes?.toLocaleString() || 0}`);
                console.log(`  Comments: ${result.comments?.toLocaleString() || 0}`);
                console.log(`  Shares: ${result.shares?.toLocaleString() || 0}`);
                console.log(`  Engagement Rate: ${result.engagement_rate?.toFixed(2) || 0}%`);
            } else {
                console.log('\nError result:');
                console.log(`  URL: ${result.post_url}`);
                console.log(`  Error: ${result.error}`);
            }
        });

        return results;

    } finally {
        await scraper.close();
    }
}

// Export for use in other modules
module.exports = { PuppeteerTikTokScraper };

// Run test if called directly
if (require.main === module) {
    testPuppeteerScraper().catch(console.error);
}
