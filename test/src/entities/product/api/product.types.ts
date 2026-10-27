export type ProductCategory = 'outerwear' | 'tops' | 'dresses'

export type Product = Readonly<{
  id: string
  name: string
  image: string
  description: string
  category: ProductCategory
  categoryLabel: string
  displayAttributes: readonly string[]
  tone: string
  priceLabel: string
}>

export type ProductCollection = Readonly<{
  products: readonly Product[]
  categories: readonly ProductCategory[]
}>
