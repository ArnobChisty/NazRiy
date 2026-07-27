import { useEffect, useState } from 'react'

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api'

type Banner = {
  id: number
  eyebrow: string
  title: string
  description: string
  desktop_image: string
  mobile_image: string
  image_alt: string
  primary_button_label: string
  primary_button_link: string
  secondary_button_label: string
  secondary_button_link: string
  theme: string
  object_position: string
}

const fallback: Banner[] = [
  { id: -1, eyebrow: 'Modern apparel · curated style', title: 'Prints made to be remembered.', description: 'Expressive florals, considered details, and an effortless silhouette for celebrations and slow afternoons.', desktop_image: '/banners/nazriy-look-1.jpeg', mobile_image: '', image_alt: 'NazRiy burgundy floral outfit', primary_button_label: 'Explore collection', primary_button_link: '/products', secondary_button_label: '', secondary_button_link: '#featured', theme: 'burgundy', object_position: 'center 42%' },
  { id: -2, eyebrow: 'The NazRiy collection', title: 'A closer look at thoughtful design.', description: 'Rich colour and delicate finishing touches turn an everyday piece into something distinctly yours.', desktop_image: '/banners/nazriy-detail.jpeg', mobile_image: '', image_alt: 'Close-up of NazRiy floral details', primary_button_label: 'Shop now', primary_button_link: '/products', secondary_button_label: '', secondary_button_link: '#featured', theme: 'forest', object_position: 'center 48%' },
]

const HeroSection = () => {
  const [slides, setSlides] = useState<Banner[]>(fallback)
  const [active, setActive] = useState(0)
  const [paused, setPaused] = useState(false)

  useEffect(() => {
    fetch(`${API_BASE}/banners/?placement=hero`)
      .then(response => response.ok ? response.json() : Promise.reject())
      .then((data: Banner[]) => { if (data.length) { setSlides(data); setActive(0) } })
      .catch(() => undefined)
  }, [])

  useEffect(() => {
    if (paused || slides.length < 2) return
    const timer = window.setInterval(() => setActive(value => (value + 1) % slides.length), 5600)
    return () => window.clearInterval(timer)
  }, [paused, slides.length])

  const change = (next: number) => setActive((next + slides.length) % slides.length)

  return <section className="editorial-hero noir-hero" id="top" aria-roledescription="carousel" aria-label="Featured NazRiy collections" onMouseEnter={() => setPaused(true)} onMouseLeave={() => setPaused(false)}>
    <div className="editorial-slides">{slides.map((slide, index) =>
      <article className={`editorial-slide theme-${slide.theme} ${index === active ? 'active' : ''}`} aria-hidden={index !== active} key={slide.id}>
        <div className="noir-hero-brand" aria-hidden="true"><span>NAZ</span><span>RIY</span></div>
        <picture>{slide.mobile_image && <source media="(max-width: 700px)" srcSet={slide.mobile_image}/>}<img src={slide.desktop_image} alt={slide.image_alt} style={{ objectPosition: slide.object_position }}/></picture>
        <div className="hero-shade"/>
        <div className="editorial-copy">
          <p className="eyebrow">{slide.eyebrow || 'Modern apparel · curated style'}</p>
          <h1>{slide.title}</h1>
          <p>{slide.description}</p>
          <div className="hero-actions"><a className="primary-button" href={slide.primary_button_link}>{slide.primary_button_label} <span>→</span></a>{slide.secondary_button_label && <a className="banner-link" href={slide.secondary_button_link}>{slide.secondary_button_label}</a>}</div>
        </div>
      </article>)}
    </div>
    {slides.length > 1 && <div className="carousel-controls noir-carousel"><button type="button" onClick={() => change(active - 1)} aria-label="Previous banner">←</button><span>{String(active + 1).padStart(2, '0')} / {String(slides.length).padStart(2, '0')}</span><button type="button" onClick={() => change(active + 1)} aria-label="Next banner">→</button></div>}
  </section>
}

export default HeroSection
