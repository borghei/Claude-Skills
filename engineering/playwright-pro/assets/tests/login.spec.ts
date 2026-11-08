import { test, expect } from '@playwright/test'

test.describe('User login with email', () => {
  test('signs in with valid email and password', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('ada@example.com')
    await page.getByLabel('Password').fill(process.env.TEST_PASSWORD ?? '')
    await page.getByRole('button', { name: 'Sign in' }).click()
    await expect(page).toHaveURL(/\/dashboard/)
    await expect(page.getByRole('heading', { name: 'Dashboard' })).toBeVisible()
  })

  test('shows an error for a wrong password', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill('ada@example.com')
    await page.getByLabel('Password').fill('wrong-password')
    await page.getByRole('button', { name: 'Sign in' }).click()
    await expect(page.getByRole('alert')).toContainText('Invalid email or password')
  })
})
