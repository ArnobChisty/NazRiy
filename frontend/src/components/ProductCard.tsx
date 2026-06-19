interface ProductCardProps {
  name: string
  category: string
  price: string
  tone: string
  shape: string
}

const ProductCard = ({ name, category, price, tone, shape }: ProductCardProps) => (
  <article className="product-card">
    <div className={`product-image ${tone}`}>
      <div className={`product-object ${shape}`} aria-hidden="true" />
      <button type="button" aria-label={`Add ${name} to favorites`}>♡</button>
    </div>
    <div className="product-meta">
      <div>
        <p>{category}</p>
        <h3>{name}</h3>
      </div>
      <strong>{price}</strong>
    </div>
  </article>
)

export default ProductCard
