import { useState } from 'react'
import Navbar from '../components/Navbar'
import HeroSection from '../components/HeroSection'
import TopCategories from '../components/TopCategories'

const HomePage = () => {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)

  const handleSubmit = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!email.trim()) return
    setSubscribed(true)
    setEmail('')
  }

  return (
    <div className="site-shell">
      <Navbar />
      <main id="main-content">
        <HeroSection />
        <TopCategories />
        <section className="story" id="about">
          <p className="eyebrow">Our approach</p>
          <h2>Objects with a quieter kind of beauty.</h2>
          <p>We choose enduring materials, useful forms, and makers who care about every detail.</p>
          <div className="story-cards" aria-label="NazRiy values">
            <article><span>01</span><h3>Natural textures</h3><p>Soft fabrics, earth tones, and materials that feel calm.</p></article>
            <article><span>02</span><h3>Useful shapes</h3><p>Pieces designed for daily use, not just display.</p></article>
            <article><span>03</span><h3>Small-batch care</h3><p>Curated collections that keep quality at the center.</p></article>
          </div>
        </section>
        <section className="promotion" aria-label="Seasonal promotion">
          <div>
            <p className="eyebrow">A slower season</p>
            <h2>Bring warmth to the everyday.</h2>
            <p>Explore tactile ceramics, natural textiles, and gentle scents selected for restful spaces.</p>
          </div>
          <a className="light-button" href="#featured">Explore the edit <span>→</span></a>
        </section>
        <section className="newsletter" aria-labelledby="newsletter-title">
          <div>
            <p className="eyebrow">Notes from NazRiy</p>
            <h2 id="newsletter-title">Thoughtful finds, occasionally.</h2>
            <p>New pieces, maker stories, and quiet inspiration—sent without the noise.</p>
          </div>
          <form className="newsletter-form" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor="email">Email address</label>
            <input id="email" type="email" placeholder="Your email address" value={email} onChange={(event) => setEmail(event.target.value)} required />
            <button type="submit">Subscribe</button>
          </form>
          {subscribed && <p className="newsletter-success">Thank you! You are now on the NazRiy update list.</p>}
        </section>
      </main>
      <footer id="contact">
        <div className="footer-intro">
          <a className="brand footer-brand" href="#top">
            <span className="brand-logo" aria-hidden="true">
              <span className="brand-logo-letter">N</span>
              <span className="brand-logo-leaf" />
            </span>
            NazRiy
          </a>
          <p>Made thoughtfully for everyday living.</p>
        </div>
        <div className="footer-column">
          <h3>Explore</h3>
          <a href="#top">Home</a><a href="#featured">Products</a><a href="#about">Our story</a>
        </div>
        <div className="footer-column">
          <h3>Contact</h3>
          <a href="mailto:hello@nazriy.com">hello@nazriy.com</a><a href="tel:+8801700000000">+880 1700-000000</a><span>Dhaka, Bangladesh</span>
        </div>
        <div className="footer-column">
          <h3>Follow</h3>
          <a href="#contact">Instagram</a><a href="#contact">Facebook</a><a href="#contact">Pinterest</a>
        </div>
        <p className="copyright">© 2026 NazRiy. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default HomePage
