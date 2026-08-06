import { useEffect, useState } from 'react'
import { getTopProducts } from '../api'
import type { TopProduct } from '../types'

const fallbackTones = ['forest', 'clay', 'sage', 'sand']

export default function TopCategories() {
  const [topProducts, setTopProducts] = useState<TopProduct[]>([])
  useEffect(() => { getTopProducts().then(setTopProducts).catch(() => undefined) }, [])
  if (topProducts.length === 0) return null

  return <section className="top-categories noir-products" id="featured" aria-labelledby="top-products-title">
    <div className="noir-section-heading">
      <div><p>Selected collection</p><h2 id="top-products-title">Top products</h2></div>
      <a href="/products">View all items <span>→</span></a>
    </div>
    <div className="category-showcase">{topProducts.map((placement, index) =>
      <a className={`category-tile ${fallbackTones[index % fallbackTones.length]}`} href={`/products/${placement.product.slug}`} aria-label={`View ${placement.product.name}`} key={placement.id}>
        {(placement.image || placement.product.primary_image) && <img src={placement.image || placement.product.primary_image} alt={placement.image_alt || placement.product.name}/>}
        <span className="category-shade product-photo-shade" aria-hidden="true"/>
        <span className="noir-product-index">{String(index + 1).padStart(2, '0')}</span>
        <span className="product-photo-link"><strong>{placement.product.name}</strong><small>View product →</small></span>
      </a>)}
    </div>
  </section>
}
