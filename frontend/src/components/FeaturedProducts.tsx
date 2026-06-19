import ProductCard from './ProductCard'

const products = [
  { name: 'The Solace Vase', category: 'Ceramics', price: '48Tk', tone: 'sand', shape: 'vase-shape' },
  { name: 'Linen Carryall', category: 'Textiles', price: '36Tk', tone: 'clay', shape: 'bag-shape' },
  { name: 'Quiet Morning Cup', category: 'Tableware', price: '24Tk', tone: 'cream', shape: 'cup-shape' },
  { name: 'Amber Glow Candle', category: 'Home fragrance', price: '29Tk', tone: 'sage', shape: 'candle-shape' },
]

const FeaturedProducts = () => (
  <section className="featured" id="featured">
    <div className="section-heading">
      <div>
        <p className="eyebrow">Selected for you</p>
        <h2>Featured pieces</h2>
      </div>
      <a href="#featured">View all products <span>→</span></a>
    </div>
    <div className="product-grid">
      {products.map((product) => <ProductCard key={product.name} {...product} />)}
    </div>
  </section>
)

export default FeaturedProducts
