import { test, expect } from '@playwright/test';

test.describe('Projects Management', () => {
  test.beforeEach(async ({ page }) => {
    // Login before each test
    await page.goto('/');
    await page.fill('input[type="email"]', 'admin@example.com');
    await page.fill('input[type="password"]', 'password');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  test('should navigate to projects list page', async ({ page }) => {
    await page.click('text=Projects >> nth=0');
    await expect(page).toHaveURL('/projects');
  });

  test('should access project creation page', async ({ page }) => {
    // From dashboard
    await page.click('text=New Project >> nth=0');
    await expect(page).toHaveURL('/projects/new');
    
    // Go back and try from projects list
    await page.goto('/projects');
    
    // Should have a "New Project" or "Create Project" button
    const createButton = page.locator('text=New Project, text=Create Project').first();
    if (await createButton.isVisible()) {
      await createButton.click();
      await expect(page).toHaveURL('/projects/new');
    }
  });

  test('should display project creation form', async ({ page }) => {
    await page.goto('/projects/new');
    
    // Should have form fields
    await expect(page.locator('input[name="name"], input[placeholder*="name" i]')).toBeVisible();
    await expect(page.locator('textarea[name="description"], textarea[placeholder*="description" i]')).toBeVisible();
    
    // Should have submit button
    await expect(page.locator('button[type="submit"], button:has-text("Create")').first()).toBeVisible();
  });

  test('should validate required fields in project creation', async ({ page }) => {
    await page.goto('/projects/new');
    
    // Try to submit without filling required fields
    const submitButton = page.locator('button[type="submit"], button:has-text("Create")').first();
    await submitButton.click();
    
    // Should show validation errors
    await expect(page.locator('text=required, text=This field is required').first()).toBeVisible();
  });

  test('should create a new project successfully', async ({ page }) => {
    await page.goto('/projects/new');
    
    // Fill in project details
    const projectName = `Test Project ${Date.now()}`;
    const projectDescription = 'This is a test project created by E2E tests';
    
    await page.fill('input[name="name"], input[placeholder*="name" i]', projectName);
    await page.fill('textarea[name="description"], textarea[placeholder*="description" i]', projectDescription);
    
    // Select project type if available
    const projectTypeSelect = page.locator('select[name="project_type"], select[name="projectType"]');
    if (await projectTypeSelect.isVisible()) {
      await projectTypeSelect.selectOption('web_application');
    }
    
    // Submit form
    const submitButton = page.locator('button[type="submit"], button:has-text("Create")').first();
    await submitButton.click();
    
    // Should redirect to project detail or projects list
    await expect(page).toHaveURL(/\/projects/);
    
    // Should show success message or project in list
    await expect(page.locator(`text=${projectName}`)).toBeVisible();
  });

  test('should display projects list', async ({ page }) => {
    await page.goto('/projects');
    
    // Should show projects page header
    await expect(page.locator('h1, h2').filter({ hasText: /projects/i })).toBeVisible();
    
    // Should show either projects or empty state
    const projectsList = page.locator('[data-testid="project-list"], .project-item, [class*="project"]');
    const emptyState = page.locator('text=No projects, text=empty');
    
    const hasProjects = await projectsList.first().isVisible();
    const isEmpty = await emptyState.first().isVisible();
    
    expect(hasProjects || isEmpty).toBeTruthy();
  });

  test('should filter projects by status', async ({ page }) => {
    await page.goto('/projects');
    
    // Look for status filter
    const statusFilter = page.locator('select[name="status"], button:has-text("Status"), [data-testid="status-filter"]');
    
    if (await statusFilter.isVisible()) {
      // Try filtering by active status
      if (await statusFilter.locator('option').first().isVisible()) {
        await statusFilter.selectOption('active');
      } else {
        await statusFilter.click();
        await page.locator('text=Active').click();
      }
      
      // Should update the list
      await page.waitForTimeout(500);
    }
  });

  test('should navigate to project detail page', async ({ page }) => {
    await page.goto('/projects');
    
    // Look for project links
    const projectLinks = page.locator('a[href*="/projects/"], .project-item a, [data-testid="project-link"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Should navigate to project detail
      await expect(page).toHaveURL(/\/projects\/[^\/]+$/);
    }
  });

  test('should display project details', async ({ page }) => {
    // First, create or find a project
    await page.goto('/projects');
    
    const projectLinks = page.locator('a[href*="/projects/"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Should show project details
      await expect(page.locator('h1, h2')).toBeVisible();
      
      // Should have project actions
      const actionButtons = page.locator('button:has-text("Start"), button:has-text("Edit"), button:has-text("Delete")');
      await expect(actionButtons.first()).toBeVisible();
    }
  });

  test('should edit project details', async ({ page }) => {
    await page.goto('/projects');
    
    const projectLinks = page.locator('a[href*="/projects/"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Look for edit button
      const editButton = page.locator('button:has-text("Edit"), button[title="Edit"], [data-testid="edit-button"]');
      
      if (await editButton.isVisible()) {
        await editButton.click();
        
        // Should show edit form
        await expect(page.locator('input[name="name"], textarea[name="description"]')).toBeVisible();
        
        // Should have save button
        await expect(page.locator('button:has-text("Save"), button:has-text("Update")')).toBeVisible();
      }
    }
  });

  test('should start a project', async ({ page }) => {
    await page.goto('/projects');
    
    const projectLinks = page.locator('a[href*="/projects/"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Look for start button (only visible for draft projects)
      const startButton = page.locator('button:has-text("Start"), [data-testid="start-button"]');
      
      if (await startButton.isVisible()) {
        await startButton.click();
        
        // Should show confirmation or update status
        await expect(page.locator('text=active, text=started')).toBeVisible();
      }
    }
  });

  test('should show project progress', async ({ page }) => {
    await page.goto('/projects');
    
    const projectLinks = page.locator('a[href*="/projects/"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Should show progress information
      await expect(page.locator('text=%, [data-testid="progress"], .progress')).toBeVisible();
    }
  });

  test('should handle project deletion', async ({ page }) => {
    await page.goto('/projects');
    
    const projectLinks = page.locator('a[href*="/projects/"]');
    const projectCount = await projectLinks.count();
    
    if (projectCount > 0) {
      await projectLinks.first().click();
      
      // Look for delete button
      const deleteButton = page.locator('button:has-text("Delete"), [data-testid="delete-button"]');
      
      if (await deleteButton.isVisible()) {
        await deleteButton.click();
        
        // Should show confirmation dialog
        const confirmButton = page.locator('button:has-text("Confirm"), button:has-text("Yes"), button:has-text("Delete")');
        const cancelButton = page.locator('button:has-text("Cancel"), button:has-text("No")');
        
        // Cancel deletion for safety
        if (await cancelButton.isVisible()) {
          await cancelButton.click();
        }
      }
    }
  });

  test('should be responsive on mobile', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    await page.goto('/projects');
    
    // Should be accessible on mobile
    await expect(page.locator('h1, h2')).toBeVisible();
    
    // Navigation should work
    const createButton = page.locator('text=New Project, text=Create').first();
    if (await createButton.isVisible()) {
      await createButton.click();
      await expect(page).toHaveURL('/projects/new');
    }
  });
});