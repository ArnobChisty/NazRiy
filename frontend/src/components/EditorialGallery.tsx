import { useMemo, useState } from 'react'
import type { Product } from '../types'
import ReliableImage from './ReliableImage'

export default function EditorialGallery({ products }: { products: Product[] }) {
  const [expanded, setExpanded] = useState(false)
  const [filter, setFilter] = useState<'all' | 'apparel' | 'new'>('all')

  const entries = useMemo(() => products.flatMap((product) => {
    const images = [product.primary_image, ...product.additional_images].filter(Boolean)
    return images.map((image, index) => ({ product, image, index }))
  }), [products])

  const filtered = filter === 'new' ? entries.slice(0, 4) : entries
  const visible = expanded ? filtered : filtered.slice(0, 6)
  if (entries.length === 0) return null

  return <section className="editorial-gallery" aria-labelledby="lookbook-title">
    <div className="editorial-gallery-heading" data-reveal>
      <div><p>Editorial archive</p><h2 id="lookbook-title">The lookbook</h2></div>
      <div className="editorial-filters" aria-label="Filter lookbook">
        <button className={filter === 'all' ? 'active' : ''} onClick={() => setFilter('all')}>All</button>
        <button className={filter === 'apparel' ? 'active' : ''} onClick={() => setFilter('apparel')}>Apparel</button>
        <button className={filter === 'new' ? 'active' : ''} onClick={() => setFilter('new')}>New</button>
      </div>
    </div>
    <div className="editorial-gallery-grid">{visible.map(({ product, image, index }, position) =>
      <a className={`editorial-gallery-card editorial-gallery-card-${position % 6}`} href={`/products/${product.slug}`} key={`${product.id}-${index}`} data-reveal>
        <ReliableImage src={image} alt={`${product.name} look ${index + 1}`} loading="lazy" decoding="async"/>
        <span><small>NAZRIY · {new Date(product.created_at).getFullYear()}</small><strong>{product.name}</strong></span>
      </a>)}
    </div>
    {filtered.length > 6 && <button className="lookbook-more" type="button" onClick={() => setExpanded(value => !value)}>{expanded ? 'Show less' : 'Load more'} <span>→</span></button>}
  </section>
}
