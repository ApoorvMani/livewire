import { test, expect } from '@playwright/test'

test('smoke: register, commit crime, train', async ({ page }) => {
  const username = `testuser_${Date.now()}`
  const password = 'password123'

  await page.goto('http://localhost:5173')
  await page.fill('input[name="username"]', username)
  await page.fill('input[name="password"]', password)
  await page.click('button[type="submit"]')
  await expect(page.locator('text=Home')).toBeVisible()

  // Go to crimes, commit a crime
  await page.click('text=Crimes')
  await page.waitForSelector('text=Pickpocket')
  await page.click('text=Go')
  await page.waitForTimeout(1000)

  // Go to gym, train
  await page.click('text=Gym')
  await page.waitForSelector('text=Train')
  await page.click('text=Train')
  await page.waitForTimeout(500)
})
