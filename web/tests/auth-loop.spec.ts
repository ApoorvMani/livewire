import { test, expect } from '@playwright/test'

test('fresh unauthenticated visit shows login form without redirect-looping', async ({ page }) => {
  await page.goto('http://localhost:5173')

  // A 401 on the initial /api/me check must NOT hard-navigate to a
  // nonexistent /login route (that causes an infinite reload loop since
  // Login is rendered conditionally in App.tsx, not routed).
  await expect(page.locator('input[name="username"]')).toBeVisible({ timeout: 5000 })
  expect(page.url()).toBe('http://localhost:5173/')
})
