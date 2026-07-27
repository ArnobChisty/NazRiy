import { useEffect, useState } from 'react'
import { getFeaturedProducts } from '../api'
import type { Product } from '../types'
import ProductCard from './ProductCard'

const FeaturedProducts = () => {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  useEffect(() => {
    getFeaturedProducts()
      .then((data) => setProducts(data.slice(0, 4)))
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  return (
    <section className="featured" id="featured">
      <div className="section-heading">
        <div>
          <p className="eyebrow">Selected for you</p>
          <h2>Featured pieces</h2>
        </div>
        <a href="/products">View all products <span>→</span></a>
      </div>
      {loading && <div className="product-grid" aria-label="Loading featured products">{[1, 2, 3, 4].map((item) => <div className="product-skeleton" key={item} />)}</div>}
      {error && <div className="inline-state">Start the Django server to see live featured products. <a href="/products">Open the catalogue</a></div>}
      {!loading && !error && <div className="product-grid">{products.map((product) => <ProductCard key={product.id} product={product} />)}</div>}
    </section>
  )
}

export default FeaturedProducts
