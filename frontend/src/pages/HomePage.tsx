import Navbar from '../components/Navbar'
import HeroSection from '../components/HeroSection'
import FeaturedProducts from '../components/FeaturedProducts'

const HomePage = () => (
  <div className="site-shell">
    <Navbar />
    <main>
      <HeroSection />
      <FeaturedProducts />
      <section className="story" id="about">
        <p className="eyebrow">Our approach</p>
        <h2>Objects with a quieter kind of beauty.</h2>
        <p>We choose enduring materials, useful forms, and makers who care about every detail.</p>
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
        <form className="newsletter-form">
          <label className="sr-only" htmlFor="email">Email address</label>
          <input id="email" type="email" placeholder="Your email address" required />
          <button type="button">Subscribe</button>
        </form>
      </section>
    </main>
    <footer id="contact">
      <div className="footer-intro">
        <a className="brand footer-brand" href="#top"><span className="brand-mark">N</span> NazRiy</a>
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

export default HomePage
