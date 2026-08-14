import { useEffect, useState } from 'react'
import { ApiError, getProduct, getProductAvailability, getRelatedProducts } from '../api'
import { trackItemEvent } from '../analytics'
import Navbar from '../components/Navbar'
import ProductArtwork from '../components/ProductArtwork'
import { formatPrice } from '../format'
import type { Product } from '../types'
import { useCart } from '../useCart'
import RecommendationSection from '../components/RecommendationSection'

interface ProductDetailsPageProps { slug: string }

const displayInches = (value: string) => Number(value).toString()

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
  const [related, setRelated] = useState<Product[]>([])
  const [checkingStock, setCheckingStock] = useState(false)

  useEffect(() => {
    let active = true
    getProduct(slug)
      .then((data) => {
        if (!active) return
        setProduct(data); setSelectedImage(data.primary_image); setSize(data.available_sizes[0] || ''); setColor(data.available_colors[0] || '')
        trackItemEvent('view_item', data)
        getRelatedProducts(data.slug).then(setRelated).catch(() => setRelated([]))
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

  const addSelectionToCart = async (goToCart = false) => {
    if (!product) return
    setCheckingStock(true)
    setNotice('')
    try {
      const availability = await getProductAvailability(product.slug)
      const freshProduct = { ...product, stock_quantity: availability.stock_quantity, in_stock: availability.in_stock }
      setProduct(freshProduct)
      if (!availability.in_stock) {
        setNotice(`${product.name} is currently out of stock.`)
        return
      }
      if (quantity > availability.stock_quantity) {
        setQuantity(availability.stock_quantity)
        setNotice(`Only ${availability.stock_quantity} item${availability.stock_quantity === 1 ? '' : 's'} remain in stock.`)
        return
      }
      addItem(freshProduct, size, color, quantity)
      trackItemEvent('add_to_cart', freshProduct, quantity)
      setNotice(`${quantity} × ${product.name} added to your cart.`)
      window.setTimeout(() => setNotice(''), 3200)
      if (goToCart) window.location.href = '/cart'
    } catch {
      setNotice('We could not confirm current stock. Please try again.')
    } finally {
      setCheckingStock(false)
    }
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
                <ProductArtwork product={product} imageUrl={selectedImage} priority />
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
              {product.size_chart.length > 0 && (
                <section className="product-size-guide" aria-labelledby="size-guide-title">
                  <div className="size-guide-heading">
                    <div><span>Measurements</span><h2 id="size-guide-title">Size guide</h2></div>
                    <small>All measurements in inches</small>
                  </div>
                  <div className="size-guide-table-wrap">
                    <table>
                      <thead><tr><th>Size</th><th>Garment bust</th><th>Top length</th><th>Best for body bust</th><th>Pant length</th></tr></thead>
                      <tbody>{product.size_chart.map((row) => (
                        <tr className={size === row.size ? 'selected' : ''} key={row.id}>
                          <th scope="row">{row.size}</th>
                          <td>{displayInches(row.garment_bust)}</td>
                          <td>{displayInches(row.length)}</td>
                          <td>{row.recommended_bust}</td>
                          <td>{displayInches(row.pant_length)}</td>
                        </tr>
                      ))}</tbody>
                    </table>
                  </div>
                  <p>Measurements may vary by 0.5–1 inch depending on fabric and production batch. If between sizes, choose the larger size.</p>
                </section>
              )}
              {product.available_colors.length > 0 && <fieldset className="option-group color-options"><legend>Color <strong>{color}</strong></legend><div>{product.available_colors.map((item) => <button className={color === item ? 'active' : ''} type="button" key={item} onClick={() => setColor(item)}><span style={{ backgroundColor: item.toLowerCase() }} />{item}</button>)}</div></fieldset>}
              <div className="quantity-row"><span>Quantity</span><div><button type="button" onClick={() => setQuantity((value) => Math.max(1, value - 1))}>−</button><strong>{quantity}</strong><button type="button" onClick={() => setQuantity((value) => Math.min(product.stock_quantity || 1, value + 1))}>+</button></div></div>
              <div className="purchase-actions"><button type="button" disabled={!product.in_stock || checkingStock} onClick={() => void addSelectionToCart()}>{checkingStock ? 'Checking stock…' : product.in_stock ? 'Add to cart' : 'Out of stock'}</button><button type="button" disabled={!product.in_stock || checkingStock} onClick={() => void addSelectionToCart(true)}>{checkingStock ? 'Checking stock…' : product.in_stock ? 'Buy now' : 'Out of stock'}</button></div>
              {notice && <p className="purchase-notice" role="status">{notice}</p>}
              <div className="detail-assurances"><span>✓ Carefully selected</span><span>✓ Easy exchange</span><span>✓ Dhaka delivery available</span></div>
            </section>
          </div>
        )}
        {!loading && product && <RecommendationSection products={related} />}
      </main>
    </div>
  )
}

export default ProductDetailsPage
