import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import SitePromotions from './SitePromotions'

const mocks = vi.hoisted(() => ({ getCampaigns: vi.fn() }))
vi.mock('../api', () => ({ getDiscountCampaigns: mocks.getCampaigns }))

const campaign = {
  id: 1, display_type: 'announcement' as const, title: 'Eid offer', message: 'Save today',
  discount_code: 'EID20', button_label: 'Shop now', button_link: '/products', image: '',
  image_alt: '', theme: 'burgundy' as const, popup_delay_seconds: 0, show_once_per_session: true,
}

describe('SitePromotions', () => {
  beforeEach(() => { sessionStorage.clear(); mocks.getCampaigns.mockReset() })

  it('shows an announcement with a copyable code and link', async () => {
    mocks.getCampaigns.mockResolvedValue([campaign])
    render(<SitePromotions />)
    expect(await screen.findByText('Eid offer')).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Shop now/ })).toHaveAttribute('href', '/products')
    await userEvent.click(screen.getByRole('button', { name: /Use code/ }))
    expect(screen.getByText('Copied')).toBeInTheDocument()
  })

  it('shows and closes a scheduled popup once per session', async () => {
    mocks.getCampaigns.mockResolvedValue([{ ...campaign, id: 2, display_type: 'popup', title: 'Private sale' }])
    render(<SitePromotions />)
    expect(await screen.findByRole('dialog')).toHaveTextContent('Private sale')
    await userEvent.click(screen.getByRole('button', { name: 'Close promotion' }))
    await waitFor(() => expect(screen.queryByRole('dialog')).not.toBeInTheDocument())
    expect(sessionStorage.getItem('nazriy-discount-popup-2')).toBe('shown')
  })
})
