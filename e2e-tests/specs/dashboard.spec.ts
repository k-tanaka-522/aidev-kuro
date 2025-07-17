import { test, expect } from '@playwright/test';

test.describe('Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should display dashboard with all sections', async ({ page }) => {
    // Check header
    await expect(page.locator('h1')).toContainText('Dashboard');
    await expect(page.locator('text=Welcome to your AgentDev Platform')).toBeVisible();
    
    // Check "New Project" button in header
    await expect(page.locator('text=New Project').first()).toBeVisible();

    // Check stats cards
    await expect(page.locator('text=Total Projects')).toBeVisible();
    await expect(page.locator('text=Active Projects')).toBeVisible();
    await expect(page.locator('text=Completed Tasks')).toBeVisible();
    await expect(page.locator('text=Active Agents')).toBeVisible();

    // Check recent projects section
    await expect(page.locator('text=Recent Projects')).toBeVisible();

    // Check quick actions
    await expect(page.locator('text=Start New Project')).toBeVisible();
    await expect(page.locator('text=Manage Agents')).toBeVisible();
    await expect(page.locator('text=Team Chat')).toBeVisible();
  });

  test('should display stats with numeric values', async ({ page }) => {
    // Wait for stats to load
    await page.waitForTimeout(1000);

    // Check that stats show numbers (even if 0)
    const statsCards = page.locator('[class*="grid"] [class*="card"]').first();
    await expect(statsCards).toBeVisible();

    // Stats should have numeric values
    await expect(page.locator('text=/^\\d+$/')).toHaveCount({ min: 4 }); // At least 4 numeric values
  });

  test('should navigate to projects page from multiple entry points', async ({ page }) => {
    // Test navigation from header button
    await page.click('text=New Project >> nth=0');
    await expect(page).toHaveURL('/projects/new');
    
    // Go back to dashboard
    await page.goto('/dashboard');

    // Test navigation from quick actions
    await page.click('text=Start New Project');
    await expect(page).toHaveURL('/projects/new');
  });

  test('should navigate to agents page', async ({ page }) => {
    await page.click('text=Manage Agents');
    await expect(page).toHaveURL('/agents');
  });

  test('should navigate to chat page', async ({ page }) => {
    await page.click('text=Team Chat');
    await expect(page).toHaveURL('/chat');
  });

  test('should show "View all" link for projects', async ({ page }) => {
    const viewAllLink = page.locator('text=View all');
    if (await viewAllLink.isVisible()) {
      await viewAllLink.click();
      await expect(page).toHaveURL('/projects');
    }
  });

  test('should display empty state when no projects exist', async ({ page }) => {
    // Wait for content to load
    await page.waitForTimeout(1000);

    // Check if empty state is shown
    const emptyState = page.locator('text=No projects');
    if (await emptyState.isVisible()) {
      await expect(page.locator('text=Get started by creating a new project.')).toBeVisible();
      
      // Should have a "New Project" button in empty state
      const newProjectButtons = page.locator('text=New Project');
      await expect(newProjectButtons).toHaveCount({ min: 1 });
    }
  });

  test('should display projects when they exist', async ({ page }) => {
    // Wait for projects to load
    await page.waitForTimeout(1000);

    // Check if projects are displayed
    const projectItems = page.locator('[class*="space-y-3"] a');
    const projectCount = await projectItems.count();

    if (projectCount > 0) {
      // Should show project information
      await expect(projectItems.first()).toBeVisible();
      
      // Each project should have a name and status
      for (let i = 0; i < Math.min(projectCount, 3); i++) {
        const project = projectItems.nth(i);
        await expect(project).toBeVisible();
      }
    }
  });

  test('should have working sidebar navigation', async ({ page }) => {
    // Test sidebar links
    await page.click('text=Projects >> nth=0');
    await expect(page).toHaveURL('/projects');

    await page.click('text=Dashboard >> nth=0');
    await expect(page).toHaveURL('/dashboard');

    await page.click('text=Agents >> nth=0');
    await expect(page).toHaveURL('/agents');

    await page.click('text=Chat >> nth=0');
    await expect(page).toHaveURL('/chat');

    await page.click('text=Artifacts >> nth=0');
    await expect(page).toHaveURL('/artifacts');
  });

  test('should show active navigation state', async ({ page }) => {
    // Dashboard should be active initially
    const dashboardLink = page.locator('text=Dashboard >> nth=0');
    await expect(dashboardLink).toHaveClass(/sidebar-link-active/);

    // Navigate to projects
    await page.click('text=Projects >> nth=0');
    
    // Projects should now be active
    const projectsLink = page.locator('text=Projects >> nth=0');
    await expect(projectsLink).toHaveClass(/sidebar-link-active/);
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Dashboard should still be accessible
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Stats should be stacked vertically on mobile
    const statsContainer = page.locator('[class*="grid-cols-1"]');
    await expect(statsContainer).toBeVisible();
  });

  test('should handle loading states gracefully', async ({ page }) => {
    // Reload to see loading states
    await page.reload();

    // Should not show error states
    await expect(page.locator('text=Error')).not.toBeVisible();
    await expect(page.locator('text=Failed')).not.toBeVisible();

    // Content should eventually load
    await expect(page.locator('h1')).toContainText('Dashboard');
  });
});