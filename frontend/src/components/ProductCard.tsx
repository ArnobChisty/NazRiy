import { useState } from 'react'
import { formatPrice } from '../format'
import type { Product } from '../types'
import ProductArtwork from './ProductArtwork'

interface ProductCardProps {
  product: Product
}

const ProductCard = ({ product }: ProductCardProps) => {
  const [favorite, setFavorite] = useState(false)

  return (
    <article className="catalog-card">
      <div className="catalog-card-image">
        <a href={`/products/${product.slug}`} aria-label={`View ${product.name}`}>
          <ProductArtwork product={product} />
        </a>
        <button
          className={favorite ? 'favorite-button active' : 'favorite-button'}
          type="button"
          aria-label={`${favorite ? 'Remove' : 'Add'} ${product.name} ${favorite ? 'from' : 'to'} favorites`}
          onClick={() => setFavorite((value) => !value)}
        >
          {favorite ? '♥' : '♡'}
        </button>
        {!product.in_stock && <span className="stock-badge">Out of stock</span>}
      </div>
      <a className="catalog-card-meta" href={`/products/${product.slug}`}>
        <div>
          <p>{product.category.name}</p>
          <h3>{product.name}</h3>
          <span>{product.short_description}</span>
        </div>
        <strong>{formatPrice(product.price)}</strong>
      </a>
    </article>
  )
}

export default ProductCard
