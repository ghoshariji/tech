import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { X, Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'
import { productService, type Product } from '@/services/product.service'
import { getApiError } from '@/lib/utils'

const schema = z.object({
  name: z.string().min(1, 'Name required'),
  sku: z.string().min(1, 'SKU required').regex(/^[A-Za-z0-9_-]+$/, 'SKU: letters, numbers, - _ only'),
  description: z.string().optional(),
  price: z.string().refine((v) => parseFloat(v) > 0, 'Price must be positive'),
  quantity: z.coerce.number().min(0, 'Quantity cannot be negative'),
  reorder_level: z.coerce.number().min(0),
  category: z.string().optional(),
})

type FormData = z.infer<typeof schema>

interface ProductModalProps {
  open: boolean
  onClose: () => void
  product?: Product | null
}

export function ProductModal({ open, onClose, product }: ProductModalProps) {
  const qc = useQueryClient()
  const isEdit = !!product

  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormData>({
    resolver: zodResolver(schema),
    defaultValues: { reorder_level: 10, quantity: 0 },
  })

  useEffect(() => {
    if (product) {
      reset({
        name: product.name, sku: product.sku,
        description: product.description || '',
        price: product.price, quantity: product.quantity,
        reorder_level: product.reorder_level, category: product.category || '',
      })
    } else {
      reset({ reorder_level: 10, quantity: 0 })
    }
  }, [product, reset])

  const mutation = useMutation({
    mutationFn: (data: FormData) =>
      isEdit ? productService.update(product!.id, data) : productService.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['products'] })
      qc.invalidateQueries({ queryKey: ['dashboard'] })
      toast.success(isEdit ? 'Product updated' : 'Product created')
      onClose()
    },
    onError: (err) => toast.error(getApiError(err)),
  })

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
      <div className="bg-card border border-border rounded-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center justify-between p-6 border-b border-border">
          <h2 className="text-lg font-semibold">{isEdit ? 'Edit Product' : 'Add Product'}</h2>
          <button onClick={onClose} className="p-1 rounded-md hover:bg-muted"><X className="h-4 w-4" /></button>
        </div>

        <form onSubmit={handleSubmit((d) => mutation.mutate(d))} className="p-6 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1.5">Product Name *</label>
              <input {...register('name')} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.name && <p className="text-xs text-destructive mt-1">{errors.name.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">SKU *</label>
              <input {...register('sku')} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.sku && <p className="text-xs text-destructive mt-1">{errors.sku.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Category</label>
              <input {...register('category')} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Price ($) *</label>
              <input {...register('price')} type="number" step="0.01" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.price && <p className="text-xs text-destructive mt-1">{errors.price.message}</p>}
            </div>

            <div>
              <label className="block text-sm font-medium mb-1.5">Quantity</label>
              <input {...register('quantity')} type="number" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
              {errors.quantity && <p className="text-xs text-destructive mt-1">{errors.quantity.message}</p>}
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1.5">Reorder Level</label>
              <input {...register('reorder_level')} type="number" className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring" />
            </div>

            <div className="col-span-2">
              <label className="block text-sm font-medium mb-1.5">Description</label>
              <textarea {...register('description')} rows={3} className="w-full px-3 py-2 border border-border rounded-lg text-sm bg-background focus:outline-none focus:ring-2 focus:ring-ring resize-none" />
            </div>
          </div>

          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose} className="flex-1 py-2 border border-border rounded-lg text-sm hover:bg-muted">Cancel</button>
            <button type="submit" disabled={isSubmitting} className="flex-1 py-2 bg-primary text-primary-foreground rounded-lg text-sm hover:bg-primary/90 disabled:opacity-60 flex items-center justify-center gap-2">
              {isSubmitting && <Loader2 className="h-4 w-4 animate-spin" />}
              {isEdit ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
