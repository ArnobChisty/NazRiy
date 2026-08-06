import { useState } from 'react'
import type { Product } from '../types'

interface ProductArtworkProps {
  product: Product
  imageUrl?: string
  compact?: boolean
}

const ProductArtwork = ({ product, imageUrl, compact = false }: ProductArtworkProps) => {
  const source = imageUrl || product.primary_image
  const [failedSource, setFailedSource] = useState('')

  if (source && source !== failedSource) {
    return <img className="product-photo" src={source} alt={product.name} onError={() => setFailedSource(source)} />
  }

  return (
    <div className={`product-artwork ${product.tone} ${compact ? 'compact' : ''}`} aria-label={`${product.name} placeholder image`}>
      <div className={`product-object ${product.shape}`} aria-hidden="true" />
    </div>
  )
}

export default ProductArtwork
