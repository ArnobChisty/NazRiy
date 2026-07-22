import type { Product } from '../types'

interface ProductArtworkProps {
  product: Product
  imageUrl?: string
  compact?: boolean
}

const ProductArtwork = ({ product, imageUrl, compact = false }: ProductArtworkProps) => {
  if (imageUrl || product.primary_image) {
    return <img className="product-photo" src={imageUrl || product.primary_image} alt={product.name} />
  }

  return (
    <div className={`product-artwork ${product.tone} ${compact ? 'compact' : ''}`} aria-label={`${product.name} placeholder image`}>
      <div className={`product-object ${product.shape}`} aria-hidden="true" />
    </div>
  )
}

export default ProductArtwork
