import type { ProductCollection } from './product.types'

/** Canonical static catalog for the presentation-only landing page. */
export const productCollection: ProductCollection = {
  categories: ['outerwear', 'tops', 'dresses'],
  products: [
    {
      id: 'linen-overshirt', name: 'Linen Overshirt',
      image: 'https://images.unsplash.com/photo-1596755389378-c31d21fd1273?auto=format&fit=crop&w=900&q=85',
      description: 'A light overshirt with a relaxed fit for everyday layering.',
      category: 'tops', categoryLabel: 'Tops',
      displayAttributes: ['Relaxed fit', 'Natural linen', 'Lightweight'], tone: 'sand', priceLabel: 'View details',
    },
    {
      id: 'structured-jacket', name: 'Structured Jacket',
      image: 'https://images.unsplash.com/photo-1551488831-00ddcb6c6bd3?auto=format&fit=crop&w=900&q=85',
      description: 'A clean structured layer designed for a polished silhouette.',
      category: 'outerwear', categoryLabel: 'Outerwear',
      displayAttributes: ['Structured cut', 'Soft cotton', 'Everyday layer'], tone: 'ink', priceLabel: 'View details',
    },
    {
      id: 'olive-dress', name: 'Olive Dress',
      image: 'https://images.unsplash.com/photo-1618932260643-eee4a2f652a6?auto=format&fit=crop&w=900&q=85',
      description: 'A fluid midi dress with an easy shape for day to evening wear.',
      category: 'dresses', categoryLabel: 'Dresses',
      displayAttributes: ['Midi length', 'Soft drape', 'Adjustable waist'], tone: 'olive', priceLabel: 'View details',
    },
  ],
}
