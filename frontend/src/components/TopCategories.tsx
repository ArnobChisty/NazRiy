import { useEffect, useState } from 'react'
import { getTopProducts } from '../api'
import type { TopProduct } from '../types'

const fallbackTones = ['forest', 'clay', 'sage', 'sand']

export default function TopCategories() {
  const [topProducts, setTopProducts] = useState<TopProduct[]>([])
  useEffect(() => { getTopProducts().then(setTopProducts).catch(() => undefined) }, [])
  if (topProducts.length === 0) return null
  return <section className="top-categories" aria-labelledby="top-products-title">
    <div className="category-section-title"><span aria-hidden="true"/><h2 id="top-products-title">Top products</h2><span aria-hidden="true"/></div>
    <div className="category-showcase">{topProducts.map((placement, index) => <a className={`category-tile ${fallbackTones[index % fallbackTones.length]}`} href={`/products/${placement.product.slug}`} aria-label={`View ${placement.product.name}`} key={placement.id}>
      {(placement.image || placement.product.primary_image) && <img src={placement.image || placement.product.primary_image} alt={placement.image_alt || placement.product.name}/>}<span className="category-shade product-photo-shade" aria-hidden="true"/><span className="product-photo-link">View product &rarr;</span>
    </a>)}</div>
  </section>
}
