import type { Product } from '../types'
import ProductCard from './ProductCard'

export default function RecommendationSection({ products, title = 'You may also like' }: { products: Product[]; title?: string }) {
  if (!products.length) return null
  return <section className="recommendation-section" aria-labelledby="recommendation-title" data-reveal>
    <div className="recommendation-heading"><p className="eyebrow">Curated for you</p><h2 id="recommendation-title">{title}</h2></div>
    <div className="recommendation-grid">{products.map(product => <ProductCard product={product} key={product.id} />)}</div>
  </section>
}
