import { useEffect, useState } from 'react'
import { getNavigationLinks } from '../api'
import type { NavigationLink } from '../types'
import { useAuth } from '../useAuth'
import { useCart } from '../useCart'

interface NavbarProps { activePage?: 'home' | 'products' | 'cart' | 'account' | 'orders' }

const SearchIcon = () => <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>
const AccountIcon = () => <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.5"/><path d="M4.5 21c.4-5 3-7.5 7.5-7.5s7.1 2.5 7.5 7.5"/></svg>
const defaultLinks: NavigationLink[] = [
  { id: -1, label: 'Shop all', url: '/products', sort_order: 1, open_in_new_tab: false },
  { id: -2, label: 'New arrivals', url: '/products?ordering=newest', sort_order: 2, open_in_new_tab: false },
  { id: -3, label: 'Women', url: '/products?category=womens-clothing', sort_order: 3, open_in_new_tab: false },
  { id: -4, label: 'Our story', url: '/#about', sort_order: 4, open_in_new_tab: false },
]

const Navbar = ({ activePage = 'home' }: NavbarProps) => {
  const { itemCount } = useCart()
  const { user, restoring, logout } = useAuth()
  const [searchOpen, setSearchOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [navigationLinks, setNavigationLinks] = useState<NavigationLink[]>(defaultLinks)
  useEffect(() => { getNavigationLinks().then(setNavigationLinks).catch(() => undefined) }, [])
  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => { event.preventDefault(); location.href = `/products${search.trim()?`?search=${encodeURIComponent(search.trim())}`:''}` }
  return <>
    <a className="skip-link" href="#main-content">Skip to main content</a>
    <header className="navbar rise-navbar">
      <a className="nav-contact" href="tel:+8801700000000"><small>Need help?</small><strong>+880 1700-000000</strong></a>
      <a className="brand rise-brand" href="/" aria-label="NazRiy home"><span className="brand-logo" aria-hidden="true"><span className="brand-logo-letter">N</span><span className="brand-logo-leaf"/></span><span>NazRiy</span></a>
      <div className="nav-actions rise-actions">
        <form className="nav-search-inline" role="search" onSubmit={handleSearch}><label className="sr-only" htmlFor="header-search">Search products</label><input id="header-search" type="search" placeholder="Search" value={search} onChange={event=>setSearch(event.target.value)}/><button aria-label="Submit search"><SearchIcon /></button></form>
        <button className="mobile-search-toggle" aria-label="Search products" aria-expanded={searchOpen} onClick={()=>setSearchOpen(value=>!value)}><SearchIcon /></button>
        {!restoring&&user?<><a className={`nav-symbol${activePage==='account'?' active':''}`} href="/account" aria-label="Open account"><AccountIcon /><small>{user.first_name||user.username}</small></a><button className="nav-logout" onClick={logout}>Log out</button></>:!restoring&&<a className="nav-symbol" href="/login" aria-label="Log in"><AccountIcon /><small>Account</small></a>}
        <a className={`nav-symbol cart-symbol${activePage==='cart'?' active':''}`} href="/cart" aria-label={`Shopping cart with ${itemCount} items`}><span aria-hidden="true">Bag</span><small>Cart</small><b>{itemCount}</b></a>
      </div>
      {searchOpen&&<form className="search-panel rise-search-panel" role="search" onSubmit={handleSearch}><label className="sr-only" htmlFor="mobile-site-search">Search products</label><input id="mobile-site-search" type="search" placeholder="Search the collection..." value={search} onChange={event=>setSearch(event.target.value)} autoFocus/><button>Search</button><button type="button" onClick={()=>setSearchOpen(false)}>Close</button></form>}
    </header>
    <nav className="category-nav" aria-label="Shop navigation">{navigationLinks.map(link => <a className={activePage==='products'&&link.url==='/products'?'active':''} href={link.url} target={link.open_in_new_tab?'_blank':undefined} rel={link.open_in_new_tab?'noreferrer':undefined} key={link.id}>{link.label}</a>)}</nav>
  </>
}

export default Navbar
