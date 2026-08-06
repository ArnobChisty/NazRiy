import { useState } from 'react'
import { formatPrice } from '../format'
import type { Product } from '../types'
import { useCart } from '../useCart'
import ProductArtwork from './ProductArtwork'

interface ProductCardProps { product: Product }

const ProductCard = ({ product }: ProductCardProps) => {
  const [favorite, setFavorite] = useState(false)
  const [added, setAdded] = useState(false)
  const { addItem } = useCart()

  const addToCart = () => {
    const size = product.available_sizes[0] || 'One Size'
    const color = product.available_colors[0] || 'Default'
    addItem(product, size, color, 1)
    setAdded(true)
    window.setTimeout(() => setAdded(false), 1300)
  }

  return (
    <article className="catalog-card" data-reveal>
      <div className="catalog-card-image">
        <a href={`/products/${product.slug}`} aria-label={`View ${product.name}`}><ProductArtwork product={product} /></a>
        <button className={favorite ? 'favorite-button active' : 'favorite-button'} type="button" aria-label={`${favorite ? 'Remove' : 'Add'} ${product.name} ${favorite ? 'from' : 'to'} favorites`} onClick={() => setFavorite(value => !value)}>{favorite ? '♥' : '♡'}</button>
        {!product.in_stock && <span className="stock-badge">Out of stock</span>}
      </div>
      <a className="catalog-card-meta" href={`/products/${product.slug}`}>
        <div><p>{product.category.name}</p><h3>{product.name}</h3><span>{product.short_description}</span></div>
        <strong>{formatPrice(product.price)}</strong>
      </a>
      <button className="catalog-add-button" type="button" disabled={!product.in_stock} onClick={addToCart}>{!product.in_stock ? 'Unavailable' : added ? 'Added to cart' : 'Add to cart'} <span>→</span></button>
    </article>
  )
}

export default ProductCard
