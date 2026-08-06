import { useEffect, useState } from 'react'
import { getFeaturedProducts, getProducts } from '../api'
import HeroSection from '../components/HeroSection'
import HomeLogin from '../components/HomeLogin'
import Navbar from '../components/Navbar'
import ProductCard from '../components/ProductCard'
import TopCategories from '../components/TopCategories'
import type { Product } from '../types'

const HomePage = () => {
  const [email, setEmail] = useState('')
  const [subscribed, setSubscribed] = useState(false)
  const [products, setProducts] = useState<Product[]>([])

  useEffect(() => {
    getFeaturedProducts()
      .then(async featured => {
        if (featured.length) return featured
        return getProducts({ search: '', category: '', min_price: '', max_price: '', size: '', color: '', ordering: 'newest' })
      })
      .then(setProducts)
      .catch(() => undefined)
  }, [])

  useEffect(() => {
    document.documentElement.classList.add('motion-ready')
    const elements = Array.from(document.querySelectorAll<HTMLElement>('[data-reveal]'))
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed')
          observer.unobserve(entry.target)
        }
      })
    }, { threshold: .12, rootMargin: '0px 0px -6% 0px' })
    elements.forEach(element => observer.observe(element))
    return () => observer.disconnect()
  }, [products.length])

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
        {products.length > 0 && <section className="home-collection" aria-labelledby="collection-title">
          <div className="home-collection-title" data-reveal><span/><div><p>Apparel</p><h2 id="collection-title">The NazRiy collection</h2></div><span/></div>
          <div className="home-product-grid">{products.slice(0, 8).map(product => <ProductCard product={product} key={product.id}/>)}</div>
          <a className="home-collection-link" href="/products" data-reveal>View the full collection <span>→</span></a>
        </section>}
        <HomeLogin />
        <section className="noir-vision" id="about">
          <div className="noir-vision-copy">
            <p className="eyebrow">Our story</p>
            <h2>Made to feel distinctly yours.</h2>
            <p>NazRiy began with a simple belief: expressive clothing should feel considered, confident, and accessible. Every piece brings together distinctive print, thoughtful detail, and silhouettes made for real life.</p>
            <a href="/products">Explore NazRiy <span>→</span></a>
          </div>
          <div className="noir-vision-image"><img src="/banners/nazriy-detail.jpeg" alt="NazRiy garment detail"/><span>NAZRIY · EST. 2024</span></div>
        </section>
        <section className="newsletter noir-newsletter" aria-labelledby="newsletter-title" data-reveal>
          <div><p className="eyebrow">Private list</p><h2 id="newsletter-title">Be first to know.</h2><p>New drops, limited pieces, and NazRiy campaign stories—delivered occasionally.</p></div>
          <form className="newsletter-form" onSubmit={handleSubmit}>
            <label className="sr-only" htmlFor="email">Email address</label>
            <input id="email" type="email" placeholder="Your email address" value={email} onChange={event => setEmail(event.target.value)} required />
            <button type="submit">Subscribe</button>
          </form>
          {subscribed && <p className="newsletter-success">You are now on the NazRiy update list.</p>}
        </section>
      </main>
      <footer id="contact">
        <div className="footer-intro"><a className="footer-brand" href="#top" aria-label="NazRiy home"><img src="/brand/nazriy-logo.jpeg" alt="NazRiy — Luxury in Budget" /></a><p>Modern apparel. Curated style.</p></div>
        <div className="footer-column"><h3>Explore</h3><a href="#top">Home</a><a href="/products">Shop</a><a href="#about">The vision</a></div>
        <div className="footer-column"><h3>Contact</h3><a href="mailto:hello@nazriy.com">hello@nazriy.com</a><span>Dhaka, Bangladesh</span></div>
        <div className="footer-column"><h3>Follow</h3><a href="#contact">Instagram</a><a href="#contact">Facebook</a><a href="#contact">Pinterest</a></div>
        <p className="copyright">© 2026 NAZRIY · EST. 2024</p>
      </footer>
    </div>
  )
}

export default HomePage
