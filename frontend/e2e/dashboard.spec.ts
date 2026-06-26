import { test, expect } from '@playwright/test';

test.describe('Dashboard and Navigation', () => {
  test('should load the dashboard and display key components', async ({ page }) => {
    await page.goto('/');

    // Check title
    await expect(page.getByText('Security Dashboard')).toBeVisible();

    // Check Stats Cards (mocked data usually loads quickly)
    await expect(page.getByRole('heading', { name: 'Total Packets' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Active Connections' })).toBeVisible();
    await expect(page.getByRole('heading', { name: 'Total Alerts' })).toBeVisible();
    
    // Check connection status
    await expect(page.getByText('REST API:')).toBeVisible();
    await expect(page.getByText('Live Feed:')).toBeVisible();
  });

  test('should open notification history modal', async ({ page }) => {
    await page.goto('/');

    // Click History button
    const historyBtn = page.getByRole('button', { name: 'History' });
    await expect(historyBtn).toBeVisible();
    await historyBtn.click();

    // Modal should appear
    const dialog = page.getByRole('dialog');
    await dialog.waitFor({ state: 'attached', timeout: 10000 });
    await expect(page.getByRole('heading', { name: 'Notification History' })).toBeAttached();
    
    // Close modal using Escape
    await page.keyboard.press('Escape');
    await expect(page.getByRole('dialog')).not.toBeVisible();
  });

  test('should navigate to connections page', async ({ page }) => {
    await page.goto('/');

    // Click Connections in sidebar
    await page.getByRole('link', { name: 'Connections' }).click();

    // Wait for route change
    await expect(page).toHaveURL(/.*\/connections/);
    await expect(page.getByRole('heading', { name: 'Active Connections' })).toBeVisible();

    // Check for datatable
    await expect(page.getByPlaceholder('Search IPs, ports, or protocols...')).toBeVisible();
  });
});
