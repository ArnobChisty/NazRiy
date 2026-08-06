import { useEffect, useState } from 'react'
import { getNavigationLinks } from '../api'
import type { NavigationLink } from '../types'
import { useAuth } from '../useAuth'
import { useCart } from '../useCart'

interface NavbarProps { activePage?: 'home' | 'products' | 'cart' | 'account' | 'orders' }

const SearchIcon = () => <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>
const AccountIcon = () => <svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="7.5" r="3.5"/><path d="M4.5 21c.4-5 3-7.5 7.5-7.5s7.1 2.5 7.5 7.5"/></svg>
const BagIcon = () => <svg aria-hidden="true" viewBox="0 0 24 24"><path d="M6.5 8.5h11l-1 12h-9z"/><path d="M9 9V6.5a3 3 0 0 1 6 0V9"/></svg>

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
  const [menuOpen, setMenuOpen] = useState(false)
  const [search, setSearch] = useState('')
  const [navigationLinks, setNavigationLinks] = useState<NavigationLink[]>(defaultLinks)

  const isActiveLink = (link: NavigationLink) => {
    if (activePage !== 'products') return false
    const target = new URL(link.url, window.location.origin)
    if (target.pathname !== window.location.pathname) return false
    const currentEntries = Array.from(new URLSearchParams(window.location.search).entries())
    const targetEntries = Array.from(target.searchParams.entries())
    return currentEntries.length === targetEntries.length
      && targetEntries.every(([key, value]) => currentEntries.some(([currentKey, currentValue]) => currentKey === key && currentValue === value))
  }

  useEffect(() => { getNavigationLinks().then(setNavigationLinks).catch(() => undefined) }, [])

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    location.href = `/products${search.trim() ? `?search=${encodeURIComponent(search.trim())}` : ''}`
  }

  return <>
    <a className="skip-link" href="#main-content">Skip to main content</a>
    <header className="navbar noir-navbar">
      <a className="noir-wordmark" href="/" aria-label="NazRiy home"><img src="/brand/nazriy-logo.jpeg" alt="NazRiy — Luxury in Budget" /></a>
      <nav className={menuOpen ? 'noir-primary-nav open' : 'noir-primary-nav'} aria-label="Primary navigation">
        {navigationLinks.map(link => <a className={isActiveLink(link) ? 'active' : ''} href={link.url} target={link.open_in_new_tab ? '_blank' : undefined} rel={link.open_in_new_tab ? 'noreferrer' : undefined} key={link.id}>{link.label}</a>)}
      </nav>
      <div className="nav-actions noir-actions">
        <button className="noir-icon-button desktop-search-toggle" aria-label="Search products" aria-expanded={searchOpen} onClick={() => setSearchOpen(value => !value)}><SearchIcon /></button>
        {!restoring && user
          ? <><a className={`noir-icon-button${activePage === 'account' ? ' active' : ''}`} href="/account" aria-label={`Open ${user.first_name || user.username}'s account`}><AccountIcon /></a><button className="nav-logout" onClick={logout}>Log out</button></>
          : !restoring && <a className="noir-icon-button" href="/login" aria-label="Log in"><AccountIcon /></a>}
        <a className={`noir-icon-button noir-cart${activePage === 'cart' ? ' active' : ''}`} href="/cart" aria-label={`Shopping cart with ${itemCount} items`}><BagIcon /><b>{itemCount}</b></a>
        <button className="noir-menu-button" type="button" aria-label="Toggle navigation" aria-expanded={menuOpen} onClick={() => setMenuOpen(value => !value)}><span/><span/></button>
      </div>
      {searchOpen && <form className="search-panel noir-search-panel" role="search" onSubmit={handleSearch}><label className="sr-only" htmlFor="site-search">Search products</label><input id="site-search" type="search" placeholder="Search the collection" value={search} onChange={event => setSearch(event.target.value)} autoFocus/><button>Search</button><button type="button" onClick={() => setSearchOpen(false)}>Close</button></form>}
    </header>
  </>
}

export default Navbar
