import { useEffect, useState } from 'react'
import { ApiError, getProduct } from '../api'
import Navbar from '../components/Navbar'
import ProductArtwork from '../components/ProductArtwork'
import { formatPrice } from '../format'
import type { Product } from '../types'
import { useCart } from '../useCart'

interface ProductDetailsPageProps { slug: string }

const ProductDetailsPage = ({ slug }: ProductDetailsPageProps) => {
  const { addItem } = useCart()
  const [product, setProduct] = useState<Product | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [missing, setMissing] = useState(false)
  const [selectedImage, setSelectedImage] = useState('')
  const [size, setSize] = useState('')
  const [color, setColor] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [notice, setNotice] = useState('')
  const [retryKey, setRetryKey] = useState(0)

  useEffect(() => {
    let active = true
    getProduct(slug)
      .then((data) => {
        if (!active) return
        setProduct(data); setSelectedImage(data.primary_image); setSize(data.available_sizes[0] || ''); setColor(data.available_colors[0] || '')
      })
      .catch((requestError: unknown) => {
        if (!active) return
        if (requestError instanceof ApiError && requestError.status === 404) setMissing(true)
        else setError('We could not connect to the NazRiy API. Please start the Django server and try again.')
      })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [slug, retryKey])

  const retry = () => { setLoading(true); setError(''); setMissing(false); setRetryKey((value) => value + 1) }

  const addSelectionToCart = (goToCart = false) => {
    if (!product) return
    addItem(product, size, color, quantity)
    setNotice(`${quantity} × ${product.name} added to your cart.`)
    window.setTimeout(() => setNotice(''), 3200)
    if (goToCart) window.location.href = '/cart'
  }

  const handleZoomMove = (event: React.MouseEvent<HTMLDivElement>) => {
    const bounds = event.currentTarget.getBoundingClientRect()
    const x = ((event.clientX - bounds.left) / bounds.width) * 100
    const y = ((event.clientY - bounds.top) / bounds.height) * 100
    event.currentTarget.style.setProperty('--zoom-x', `${x}%`)
    event.currentTarget.style.setProperty('--zoom-y', `${y}%`)
  }

  const images = product ? [product.primary_image, ...product.additional_images].filter(Boolean).slice(0, 4) : []

  return (
    <div className="site-shell">
      <Navbar activePage="products" />
      <main id="main-content" className="details-page">
        <nav className="breadcrumbs" aria-label="Breadcrumb"><a href="/">Home</a><span>/</span><a href="/products">Products</a>{product && <><span>/</span><span>{product.name}</span></>}</nav>
        {loading && <div className="details-loading"><div className="product-skeleton" /><div><i /><i /><i /><i /></div></div>}
        {!loading && missing && <div className="page-state"><span>404</span><h1>That piece has moved.</h1><p>The product may have been removed or the address is incorrect.</p><a className="primary-button" href="/products">Return to products →</a></div>}
        {!loading && error && <div className="page-state error-state"><span>!</span><h1>We cannot load this piece.</h1><p>{error}</p><button type="button" onClick={retry}>Try again</button></div>}
        {!loading && product && (
          <div className="product-details-layout">
            <section className="product-gallery" aria-label={`${product.name} images`}>
              <div className={selectedImage ? 'gallery-main zoomable' : 'gallery-main'} onMouseMove={handleZoomMove}>
                <ProductArtwork product={product} imageUrl={selectedImage} />
                {selectedImage && <span className="zoom-hint">Hover to zoom</span>}
              </div>
              <div className="gallery-thumbnails">
                {(images.length ? images : ['', '', '', '']).map((image, index) => <button className={selectedImage === image ? 'active' : ''} type="button" key={`${image}-${index}`} onClick={() => setSelectedImage(image)} aria-label={`View image ${index + 1}`}><ProductArtwork product={product} imageUrl={image} compact /></button>)}
              </div>
            </section>
            <section className="product-information">
              <p className="eyebrow">{product.category.name}</p>
              <h1>{product.name}</h1>
              <p className="detail-price">{formatPrice(product.price)}</p>
              <p className="detail-description">{product.description}</p>
              <div className={product.in_stock ? 'availability in-stock' : 'availability'}>{product.in_stock ? `${product.stock_quantity} available` : 'Currently out of stock'}</div>
              {product.available_sizes.length > 0 && <fieldset className="option-group"><legend>Size <strong>{size}</strong></legend><div>{product.available_sizes.map((item) => <button className={size === item ? 'active' : ''} type="button" key={item} onClick={() => setSize(item)}>{item}</button>)}</div></fieldset>}
              {product.available_colors.length > 0 && <fieldset className="option-group color-options"><legend>Color <strong>{color}</strong></legend><div>{product.available_colors.map((item) => <button className={color === item ? 'active' : ''} type="button" key={item} onClick={() => setColor(item)}><span style={{ backgroundColor: item.toLowerCase() }} />{item}</button>)}</div></fieldset>}
              <div className="quantity-row"><span>Quantity</span><div><button type="button" onClick={() => setQuantity((value) => Math.max(1, value - 1))}>−</button><strong>{quantity}</strong><button type="button" onClick={() => setQuantity((value) => Math.min(product.stock_quantity || 1, value + 1))}>+</button></div></div>
              <div className="purchase-actions"><button type="button" disabled={!product.in_stock} onClick={() => addSelectionToCart()}>Add to cart</button><button type="button" disabled={!product.in_stock} onClick={() => addSelectionToCart(true)}>Buy now</button></div>
              {notice && <p className="purchase-notice" role="status">{notice}</p>}
              <div className="detail-assurances"><span>✓ Carefully selected</span><span>✓ Easy exchange</span><span>✓ Dhaka delivery available</span></div>
            </section>
          </div>
        )}
      </main>
    </div>
  )
}

export default ProductDetailsPage
