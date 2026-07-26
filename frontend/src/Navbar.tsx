const Navbar = () => (
  <header className="navbar">
    <a className="brand" href="#top" aria-label="NazRiy home">
      <span className="brand-mark">N</span>
      <span>NazRiy</span>
    </a>

    <nav className="nav-links" aria-label="Main navigation">
      <a className="active" href="#top">Home</a>
      <a href="#featured">Products</a>
      <a href="#about">About</a>
      <a href="#contact">Contact</a>
    </nav>

    <div className="nav-actions">
      <button className="text-button" type="button">Log in</button>
      <button className="cart-button" type="button" aria-label="Shopping cart with 2 items">
        Cart <span>2</span>
      </button>
    </div>
  </header>
)

export default Navbar
