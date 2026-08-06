import { useEffect, useState } from 'react'
import { getCategories, getProducts } from '../api'
import Navbar from '../components/Navbar'
import ProductCard from '../components/ProductCard'
import type { Category, Product, ProductFilters } from '../types'

const initialFilters = (): ProductFilters => {
  const params = new URLSearchParams(window.location.search)
  return {
    search: params.get('search') || '', category: params.get('category') || '',
    min_price: '', max_price: '', size: '', color: '', ordering: params.get('ordering') || 'newest',
  }
}

const navigationFilters = (): ProductFilters => {
  const params = new URLSearchParams(window.location.search)
  return {
    search: '', category: params.get('category') || '',
    min_price: '', max_price: '', size: '', color: '', ordering: params.get('ordering') || 'newest',
  }
}

const ProductListingPage = () => {
  const [filters, setFilters] = useState<ProductFilters>(initialFilters)
  const [appliedFilters, setAppliedFilters] = useState<ProductFilters>(initialFilters)
  const [products, setProducts] = useState<Product[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [filtersOpen, setFiltersOpen] = useState(false)
  const [retryKey, setRetryKey] = useState(0)
  const pageParams = new URLSearchParams(window.location.search)
  const isWomenView = pageParams.get('category') === 'womens-clothing'
  const isNewArrivalsView = !isWomenView && pageParams.has('ordering') && pageParams.get('ordering') === 'newest'
  const catalogueIntro = isWomenView
    ? { eyebrow: "Women's collection", title: 'Designed for her.', description: 'Explore the complete NazRiy womenswear edit, from expressive prints to considered everyday silhouettes.' }
    : isNewArrivalsView
      ? { eyebrow: 'New arrivals', title: 'The latest from NazRiy.', description: 'Discover the newest pieces to join the collection, presented with the latest additions first.' }
      : { eyebrow: 'Shop all', title: 'The complete collection.', description: 'Explore every available NazRiy piece in one place, with filters to help you find your preferred style.' }

  useEffect(() => {
    let active = true
    getProducts(appliedFilters)
      .then((data) => { if (active) setProducts(data) })
      .catch(() => { if (active) setError('We could not load the collection. Make sure the Django server is running, then try again.') })
      .finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [appliedFilters, retryKey])

  useEffect(() => { getCategories().then(setCategories).catch(() => undefined) }, [])

  const applyFilters = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setLoading(true); setError('')
    setAppliedFilters(filters)
    setFiltersOpen(false)
  }

  const resetFilters = () => {
    const reset = navigationFilters()
    setLoading(true); setError('')
    setFilters(reset)
    setAppliedFilters(reset)
  }

  const update = (field: keyof ProductFilters, value: string) => setFilters((current) => ({ ...current, [field]: value }))
  const retry = () => { setLoading(true); setError(''); setRetryKey((value) => value + 1) }

  return (
    <div className="site-shell">
      <Navbar activePage="products" />
      <main id="main-content" className="catalog-page">
        <header className="page-banner">
          <div><p className="eyebrow">{catalogueIntro.eyebrow}</p><h1>{catalogueIntro.title}</h1></div>
          <p>{catalogueIntro.description}</p>
        </header>
        <div className="catalog-toolbar">
          <button className="filter-toggle" type="button" onClick={() => setFiltersOpen((value) => !value)}>Filters</button>
          <p>{loading ? 'Finding pieces…' : `${products.length} ${products.length === 1 ? 'piece' : 'pieces'}`}</p>
          <label>Sort
            <select value={filters.ordering} onChange={(event) => { setLoading(true); setError(''); update('ordering', event.target.value); setAppliedFilters((current) => ({ ...current, ordering: event.target.value })) }}>
              <option value="newest">Newest</option><option value="price_asc">Price: low to high</option><option value="price_desc">Price: high to low</option><option value="name">Name</option>
            </select>
          </label>
        </div>
        <div className="catalog-layout">
          <aside className={filtersOpen ? 'filters-panel open' : 'filters-panel'}>
            <form onSubmit={applyFilters}>
              <div className="filter-heading"><h2>Filters</h2><button type="button" onClick={resetFilters}>Reset all</button></div>
              <label>Search<input type="search" value={filters.search} onChange={(event) => update('search', event.target.value)} placeholder="Product name" /></label>
              <label>Category<select value={filters.category} onChange={(event) => update('category', event.target.value)}><option value="">All categories</option>{categories.map((category) => <option key={category.id} value={category.slug}>{category.name} ({category.product_count})</option>)}</select></label>
              <fieldset><legend>Price range</legend><div className="price-inputs"><input type="number" min="0" placeholder="Min" value={filters.min_price} onChange={(event) => update('min_price', event.target.value)} /><input type="number" min="0" placeholder="Max" value={filters.max_price} onChange={(event) => update('max_price', event.target.value)} /></div></fieldset>
              <label>Size<select value={filters.size} onChange={(event) => update('size', event.target.value)}><option value="">All sizes</option>{['Small', 'Medium', 'Large', 'One Size', '250 ml', '350 ml'].map((size) => <option key={size}>{size}</option>)}</select></label>
              <label>Color<select value={filters.color} onChange={(event) => update('color', event.target.value)}><option value="">All colors</option>{['Sand', 'Clay', 'Cream', 'Sage', 'Olive', 'Amber'].map((color) => <option key={color}>{color}</option>)}</select></label>
              <button className="apply-button" type="submit">Apply filters</button>
            </form>
          </aside>
          <section className="catalog-results" aria-live="polite">
            {loading && <div className="catalog-grid">{Array.from({ length: 6 }, (_, index) => <div className="product-skeleton" key={index} />)}</div>}
            {!loading && error && <div className="page-state error-state"><span>!</span><h2>The collection is taking a pause.</h2><p>{error}</p><button type="button" onClick={retry}>Try again</button></div>}
            {!loading && !error && products.length === 0 && <div className="page-state"><span>⌕</span><h2>No pieces match those filters.</h2><p>Try a wider price range or clear the filters to see the full collection.</p><button type="button" onClick={resetFilters}>Clear filters</button></div>}
            {!loading && !error && products.length > 0 && <div className="catalog-grid">{products.map((product) => <ProductCard key={product.id} product={product} />)}</div>}
          </section>
        </div>
      </main>
    </div>
  )
}

export default ProductListingPage
