import { useEffect, useMemo, useState } from 'react'
import { getDiscountCampaigns } from '../api'
import type { DiscountCampaign } from '../types'
import ReliableImage from './ReliableImage'

const sessionKey = (id: number) => `nazriy-discount-popup-${id}`

export default function SitePromotions() {
  const [campaigns, setCampaigns] = useState<DiscountCampaign[]>([])
  const [popupOpen, setPopupOpen] = useState(false)
  const [copiedCode, setCopiedCode] = useState('')
  const announcement = useMemo(() => campaigns.find(item => item.display_type === 'announcement'), [campaigns])
  const popup = useMemo(() => campaigns.find(item => item.display_type === 'popup'), [campaigns])

  useEffect(() => {
    let active = true
    const load = () => getDiscountCampaigns().then(items => { if (active) setCampaigns(items) }).catch(() => undefined)
    const idleId = window.requestIdleCallback?.(() => void load(), { timeout: 1200 })
    const timerId = idleId === undefined ? window.setTimeout(() => void load(), 0) : undefined
    return () => {
      active = false
      if (idleId !== undefined) window.cancelIdleCallback?.(idleId)
      if (timerId !== undefined) window.clearTimeout(timerId)
    }
  }, [])

  useEffect(() => {
    if (!popup) return
    if (popup.show_once_per_session && window.sessionStorage.getItem(sessionKey(popup.id))) return
    const timer = window.setTimeout(() => {
      setPopupOpen(true)
      if (popup.show_once_per_session) window.sessionStorage.setItem(sessionKey(popup.id), 'shown')
    }, Math.max(0, popup.popup_delay_seconds) * 1000)
    return () => window.clearTimeout(timer)
  }, [popup])

  const copyCode = async (code: string) => {
    try { await navigator.clipboard.writeText(code) } catch { /* clipboard is optional */ }
    setCopiedCode(code)
    window.setTimeout(() => setCopiedCode(''), 1800)
  }

  return <>
    {announcement && <section className={`discount-announcement campaign-${announcement.theme}`} aria-label="Current promotion">
      <div><strong>{announcement.title}</strong>{announcement.message && <span>{announcement.message}</span>}</div>
      {announcement.discount_code && <button type="button" onClick={() => copyCode(announcement.discount_code)}><small>{copiedCode === announcement.discount_code ? 'Copied' : 'Use code'}</small>{announcement.discount_code}</button>}
      {announcement.button_label && <a href={announcement.button_link || '/products'}>{announcement.button_label} <span>→</span></a>}
    </section>}

    {popup && popupOpen && <div className="discount-popup-backdrop" role="presentation" onMouseDown={event => { if (event.target === event.currentTarget) setPopupOpen(false) }}>
      <section className={`discount-popup campaign-${popup.theme}`} role="dialog" aria-modal="true" aria-labelledby={`discount-title-${popup.id}`}>
        <button className="discount-popup-close" type="button" onClick={() => setPopupOpen(false)} aria-label="Close promotion">×</button>
        {popup.image && <ReliableImage src={popup.image} alt={popup.image_alt} decoding="async" />}
        <div className="discount-popup-copy">
          <small>Exclusive NazRiy offer</small>
          <h2 id={`discount-title-${popup.id}`}>{popup.title}</h2>
          {popup.message && <p>{popup.message}</p>}
          {popup.discount_code && <button className="discount-code" type="button" onClick={() => copyCode(popup.discount_code)}><span>{copiedCode === popup.discount_code ? 'Code copied' : 'Click to copy'}</span><strong>{popup.discount_code}</strong></button>}
          {popup.button_label && <a href={popup.button_link || '/products'}>{popup.button_label} <span>→</span></a>}
        </div>
      </section>
    </div>}
  </>
}
