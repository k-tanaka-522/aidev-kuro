import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display login page when not authenticated', async ({ page }) => {
    await expect(page.locator('h2')).toContainText('Sign in to AgentDev Platform');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('should show validation errors for invalid login', async ({ page }) => {
    // Try to login with empty fields
    await page.click('button[type="submit"]');
    
    await expect(page.locator('text=Invalid email address')).toBeVisible();
    await expect(page.locator('text=Password must be at least 8 characters')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('input[type="email"]', 'wrong@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');

    await expect(page.locator('text=Invalid credentials')).toBeVisible();
  });

  test('should login successfully with valid credentials', async ({ page }) => {
    // Fill in demo credentials
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password');
    
    // Click login button
    await page.click('button[type="submit"]');

    // Should redirect to dashboard
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('text=AgentDev Platform')).toBeVisible();
  });

  test('should toggle password visibility', async ({ page }) => {
    const passwordInput = page.locator('input[type="password"]');
    const toggleButton = page.locator('button[type="button"]').last();

    // Password should be hidden initially
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Click toggle button
    await toggleButton.click();

    // Password should be visible
    await expect(page.locator('input[type="text"]')).toBeVisible();

    // Click toggle button again
    await toggleButton.click();

    // Password should be hidden again
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await expect(page).toHaveURL('/dashboard');

    // Click logout button
    await page.click('button[title="Logout"]');

    // Should redirect back to login
    await expect(page).toHaveURL('/login');
    await expect(page.locator('h2')).toContainText('Sign in to AgentDev Platform');
  });

  test('should redirect to login when accessing protected route without auth', async ({ page }) => {
    // Try to access protected route directly
    await page.goto('/projects');

    // Should be redirected to login
    await expect(page).toHaveURL('/login');
  });

  test('should persist authentication across page reloads', async ({ page }) => {
    // Login first
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');

    await expect(page).toHaveURL('/dashboard');

    // Reload the page
    await page.reload();

    // Should still be on dashboard (authenticated)
    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});