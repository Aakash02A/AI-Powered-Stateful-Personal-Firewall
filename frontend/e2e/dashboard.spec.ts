import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E', () => {
  test('loads dashboard and navigates', async ({ page }) => {
    await page.route('**/api/v1/stats', async route => {
      await route.fulfill({ json: { status: 'success', data: { total_packets: 1000, active_connections: 5, total_alerts: 2, blocked_ips: 1 } } });
    });
    await page.route('**/api/v1/protocols', async route => {
      await route.fulfill({ json: { status: 'success', data: { TCP: 800, UDP: 200 } } });
    });

    await page.goto('http://localhost:5173/');
    
    await expect(page.locator('text=Status:').first()).toBeVisible();

    await page.click('text=Active Connections');
    await expect(page.locator('text=Active Connections').first()).toBeVisible();
    
    const html = page.locator('html');
    const isDark = await html.evaluate(node => node.classList.contains('light') === false);
    
    await page.click('button[aria-label="Toggle Theme"]');
    
    if (isDark) {
      await expect(html).toHaveClass(/light/);
    } else {
      await expect(html).not.toHaveClass(/light/);
    }
  });
});
