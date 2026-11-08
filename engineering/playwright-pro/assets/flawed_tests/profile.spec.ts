// Deliberately flawed spec for test_analyzer.py: fixed sleeps and brittle CSS locators.
import { test, expect } from '@playwright/test'

test('update profile name', async ({ page }) => {
  await page.goto('/settings/profile')
  await page.waitForTimeout(3000)
  await page.locator('div.form > input:nth-child(2)').fill('Ada')
  await page.locator('#save-btn').click()
  await page.waitForTimeout(2000)
  expect(await page.locator('.toast').isVisible()).toBe(true)
})
