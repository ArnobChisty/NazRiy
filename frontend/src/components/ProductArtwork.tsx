import { useEffect, useRef, useState } from 'react'
import type { Product } from '../types'

interface ProductArtworkProps {
  product: Product
  imageUrl?: string
  compact?: boolean
  priority?: boolean
}

const ProductArtwork = ({ product, imageUrl, compact = false, priority = false }: ProductArtworkProps) => {
  const source = imageUrl || product.primary_image
  const [retryState, setRetryState] = useState(() => ({ source, count: 0, failed: false }))
  const retryTimer = useRef<number | undefined>(undefined)
  const currentRetry = retryState.source === source ? retryState : { source, count: 0, failed: false }

  useEffect(() => {
    window.clearTimeout(retryTimer.current)
    const retryWhenOnline = () => setRetryState({ source, count: 0, failed: false })
    window.addEventListener('online', retryWhenOnline)
    return () => {
      window.clearTimeout(retryTimer.current)
      window.removeEventListener('online', retryWhenOnline)
    }
  }, [source])

  const retryImage = () => {
    if (currentRetry.count >= 3) {
      setRetryState({ source, count: currentRetry.count, failed: true })
      retryTimer.current = window.setTimeout(() => {
        setRetryState({ source, count: 0, failed: false })
      }, 10_000)
      return
    }
    window.clearTimeout(retryTimer.current)
    const delays = [350, 900, 1800]
    retryTimer.current = window.setTimeout(() => {
      setRetryState({ source, count: currentRetry.count + 1, failed: false })
    }, delays[currentRetry.count])
  }

  if (source && !currentRetry.failed) {
    return <img key={`${source}:${currentRetry.count}`} className="product-photo" src={source} alt={product.name} loading={priority || compact ? 'eager' : 'lazy'} fetchPriority={priority ? 'high' : 'auto'} decoding="async" onLoad={() => window.clearTimeout(retryTimer.current)} onError={retryImage} />
  }

  return (
    <div className={`product-artwork ${product.tone} ${compact ? 'compact' : ''}`} aria-label={`${product.name} placeholder image`}>
      <div className={`product-object ${product.shape}`} aria-hidden="true" />
    </div>
  )
}

export default ProductArtwork
