import { useEffect, useState } from 'react'
import type { Banner } from '../types'
import ReliableImage from './ReliableImage'

interface HeroSectionProps {
  banners?: Banner[]
  loading?: boolean
}

const HeroSection = ({ banners = [], loading = false }: HeroSectionProps) => {
  const [active, setActive] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    if (paused || banners.length < 2) return
    const timer = window.setInterval(() => setActive(value => (value + 1) % banners.length), 5600)
    return () => window.clearInterval(timer)
  }, [paused, banners.length])

  useEffect(() => {
    if (banners.length < 2) return
    const next = banners[(active + 1) % banners.length]
    const timer = window.setTimeout(() => {
      const image = new Image()
      image.src = next.desktop_image
    }, 2500)
    return () => window.clearTimeout(timer)
  }, [active, banners])

  if (loading || banners.length === 0) {
    return <section className="editorial-hero noir-hero hero-loading" id="top" aria-label="Loading featured NazRiy collection" aria-busy={loading}>
      <div className="hero-loading-copy" aria-hidden="true"><i/><i/><i/><i/></div>
      <span className="sr-only">{loading ? 'Loading featured collection.' : 'No featured banner is currently active.'}</span>
    </section>
  }

  const currentActive = active % banners.length
  const change = (next: number) => setActive((next + banners.length) % banners.length)

  return <section className="editorial-hero noir-hero" id="top" aria-roledescription="carousel" aria-label="Featured NazRiy collections" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
    <div className="editorial-slides">{banners.map((slide, index) =>
      <article className={`editorial-slide theme-${slide.theme} ${index === currentActive ? 'active' : ''}`} aria-hidden={index !== currentActive} key={slide.id}>
        <div className="noir-hero-brand" aria-hidden="true"><span>NAZ</span><span>RIY</span></div>
        <picture>{index === currentActive && <>{slide.mobile_image && <source media="(max-width: 700px)" srcSet={slide.mobile_image}/>}<ReliableImage src={slide.desktop_image} alt={slide.image_alt} style={{ objectPosition: slide.object_position }} loading="eager" fetchPriority={index === 0 ? 'high' : 'auto'} decoding="async"/></>}</picture>
        <div className="hero-shade"/>
        <div className="editorial-copy">
          <p className="eyebrow">{slide.eyebrow || 'Modern apparel · curated style'}</p>
          <h1>{slide.title}</h1>
          <p>{slide.description}</p>
          <div className="hero-actions"><a className="primary-button" href={slide.primary_button_link}>{slide.primary_button_label} <span>→</span></a>{slide.secondary_button_label && <a className="banner-link" href={slide.secondary_button_link}>{slide.secondary_button_label}</a>}</div>
        </div>
      </article>)}
    </div>
    {banners.length > 1 && <div className="carousel-controls noir-carousel"><button type="button" onClick={() => change(currentActive - 1)} aria-label="Previous banner">←</button><span>{String(currentActive + 1).padStart(2, '0')} / {String(banners.length).padStart(2, '0')}</span><button type="button" onClick={() => change(currentActive + 1)} aria-label="Next banner">→</button></div>}
  </section>
}

export default HeroSection
