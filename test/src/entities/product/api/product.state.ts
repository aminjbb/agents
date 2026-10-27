import type { ProductCollection } from './product.types'

/** UI-facing lifecycle for the canonical product catalog. */
export type ProductCollectionState =
  | Readonly<{ status: 'idle' }>
  | Readonly<{ status: 'loading'; data?: ProductCollection }>
  | Readonly<{ status: 'success'; data: ProductCollection }>
  | Readonly<{ status: 'error'; error: string; data?: ProductCollection }>

export const productCollectionState = {
  idle: (): ProductCollectionState => ({ status: 'idle' }),
  loading: (data?: ProductCollection): ProductCollectionState =>
    data ? { status: 'loading', data } : { status: 'loading' },
  success: (data: ProductCollection): ProductCollectionState => ({
    status: 'success',
    data,
  }),
  error: (error: string, data?: ProductCollection): ProductCollectionState =>
    data ? { status: 'error', error, data } : { status: 'error', error },
} as const
