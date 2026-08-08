import { useState } from 'react'
import { getProductAvailability } from '../api'
import { trackItemEvent } from '../analytics'
import { formatPrice } from '../format'
import type { Product } from '../types'
import { useCart } from '../useCart'
import ProductArtwork from './ProductArtwork'

interface ProductCardProps { product: Product; allowAddToCart?: boolean }

const ProductCard = ({ product, allowAddToCart = true }: ProductCardProps) => {
  const [favorite, setFavorite] = useState(false)
  const [added, setAdded] = useState(false)
  const [checking, setChecking] = useState(false)
  const [stockError, setStockError] = useState('')
  const { addItem } = useCart()

  const addToCart = async () => {
    setChecking(true)
    setStockError('')
    try {
      const availability = await getProductAvailability(product.slug)
      if (!availability.in_stock) {
        setStockError('Out of stock')
        return
      }
      const freshProduct = { ...product, stock_quantity: availability.stock_quantity, in_stock: true }
      const size = product.available_sizes[0] || 'One Size'
      const color = product.available_colors[0] || ''
      addItem(freshProduct, size, color, 1)
      trackItemEvent('add_to_cart', freshProduct)
      setAdded(true)
      window.setTimeout(() => setAdded(false), 1300)
    } catch {
      setStockError('Please try again')
    } finally {
      setChecking(false)
    }
  }

  const outOfStock = !product.in_stock || stockError === 'Out of stock'

  return (
    <article className="catalog-card" data-reveal>
      <div className="catalog-card-image">
        <a href={`/products/${product.slug}`} aria-label={`View ${product.name}`}><ProductArtwork product={product} /></a>
        <button className={favorite ? 'favorite-button active' : 'favorite-button'} type="button" aria-label={`${favorite ? 'Remove' : 'Add'} ${product.name} ${favorite ? 'from' : 'to'} favorites`} onClick={() => setFavorite(value => !value)}>{favorite ? '♥' : '♡'}</button>
        {outOfStock && <span className="stock-badge">Out of stock</span>}
      </div>
      <a className="catalog-card-meta" href={`/products/${product.slug}`}>
        <div><p>{product.category.name}</p><h3>{product.name}</h3><span>{product.short_description}</span></div>
        <strong>{formatPrice(product.price)}</strong>
      </a>
      {allowAddToCart ? (
        <button className="catalog-add-button" type="button" disabled={outOfStock || checking} onClick={() => void addToCart()}>{outOfStock ? 'Out of stock' : checking ? 'Checking stock…' : added ? 'Added to cart' : stockError || 'Add to cart'} <span>→</span></button>
      ) : (
        <a className="catalog-add-button" href={`/products/${product.slug}`}>{outOfStock ? 'View product' : 'Choose size & colour'} <span>→</span></a>
      )}
    </article>
  )
}

export default ProductCard
