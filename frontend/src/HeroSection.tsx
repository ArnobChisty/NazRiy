const HeroSection = () => (
  <section className="hero" id="top">
    <div className="hero-copy">
      <p className="eyebrow">Thoughtfully made · Naturally yours</p>
      <h1>Everyday pieces,<br />made with intention.</h1>
      <p className="hero-description">
        Discover a curated collection of timeless essentials designed to bring
        warmth, ease, and quiet beauty into your day.
      </p>
      <a className="primary-button" href="#featured">Shop the collection <span>→</span></a>
    </div>

    <div className="hero-art" aria-label="Decorative product display">
      <div className="sun" />
      <div className="arch arch-back" />
      <div className="arch arch-front" />
      <div className="vase"><span /><i /><b /></div>
      <div className="bottle"><span /></div>
      <p>Simple forms<br />honest materials</p>
    </div>
  </section>
)

export default HeroSection
