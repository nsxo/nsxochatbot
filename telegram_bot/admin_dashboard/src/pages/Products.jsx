import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon,
  CurrencyDollarIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { api } from '../services/api'

const ProductCard = ({ product, onEdit, onToggle, onDelete }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="card p-6 hover:shadow-lg transition-shadow"
  >
    <div className="flex items-start justify-between">
      <div className="flex-1">
        <div className="flex items-center space-x-2">
          <h3 className="text-lg font-semibold text-gray-900">{product.label}</h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            product.is_active 
              ? 'bg-green-100 text-green-800' 
              : 'bg-gray-100 text-gray-800'
          }`}>
            {product.is_active ? 'Active' : 'Inactive'}
          </span>
        </div>
        
        <div className="mt-2 space-y-1">
          <p className="text-sm text-gray-600">
            {product.item_type === 'credits' ? '💰' : '⏰'} {product.amount} {product.item_type}
          </p>
          {product.description && (
            <p className="text-sm text-gray-500">{product.description}</p>
          )}
          <p className="text-xs text-gray-400">
            Stripe: {product.stripe_price_id || 'Not configured'}
          </p>
        </div>
      </div>
      
      <div className="flex items-center space-x-2">
        <button
          onClick={() => onToggle(product)}
          className={`p-2 rounded-md ${
            product.is_active
              ? 'text-gray-400 hover:text-gray-600'
              : 'text-green-400 hover:text-green-600'
          }`}
          title={product.is_active ? 'Deactivate' : 'Activate'}
        >
          {product.is_active ? <EyeSlashIcon className="h-5 w-5" /> : <EyeIcon className="h-5 w-5" />}
        </button>
        
        <button
          onClick={() => onEdit(product)}
          className="p-2 text-blue-400 hover:text-blue-600 rounded-md"
          title="Edit"
        >
          <PencilIcon className="h-5 w-5" />
        </button>
        
        <button
          onClick={() => onDelete(product)}
          className="p-2 text-red-400 hover:text-red-600 rounded-md"
          title="Delete"
        >
          <TrashIcon className="h-5 w-5" />
        </button>
      </div>
    </div>
  </motion.div>
)

const ProductForm = ({ product, onSave, onCancel }) => {
  const { register, handleSubmit, formState: { errors } } = useForm({
    defaultValues: product || {
      label: '',
      amount: '',
      item_type: 'credits',
      description: '',
      stripe_price_id: '',
      is_active: true
    }
  })

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card p-6"
    >
      <h3 className="text-lg font-semibold text-gray-900 mb-6">
        {product ? 'Edit Product' : 'Create New Product'}
      </h3>
      
      <form onSubmit={handleSubmit(onSave)} className="space-y-6">
        <div>
          <label className="label">Product Label</label>
          <input
            {...register('label', { required: 'Label is required' })}
            className="input"
            placeholder="e.g., Premium Pack - 50 Credits"
          />
          {errors.label && (
            <p className="mt-1 text-sm text-red-600">{errors.label.message}</p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="label">Type</label>
            <select {...register('item_type')} className="input">
              <option value="credits">Credits Package</option>
              <option value="time">Time Session</option>
            </select>
          </div>

          <div>
            <label className="label">Amount</label>
            <input
              {...register('amount', { required: 'Amount is required', min: 1 })}
              type="number"
              className="input"
              placeholder="50"
            />
            {errors.amount && (
              <p className="mt-1 text-sm text-red-600">{errors.amount.message}</p>
            )}
          </div>
        </div>

        <div>
          <label className="label">Description (Optional)</label>
          <textarea
            {...register('description')}
            className="textarea"
            rows={3}
            placeholder="Brief description of this package..."
          />
        </div>

        <div>
          <label className="label">Stripe Price ID (Optional)</label>
          <input
            {...register('stripe_price_id')}
            className="input"
            placeholder="price_xxxxxxxxxxxxxxxxxx"
          />
          <p className="mt-1 text-sm text-gray-500">
            Leave empty if you haven't created this in Stripe yet
          </p>
        </div>

        <div>
          <label className="flex items-center">
            <input
              {...register('is_active')}
              type="checkbox"
              className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
            />
            <span className="ml-2 text-sm text-gray-700">Active (visible to users)</span>
          </label>
        </div>

        <div className="flex justify-end space-x-3">
          <button
            type="button"
            onClick={onCancel}
            className="btn-secondary"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="btn-primary"
          >
            {product ? 'Update Product' : 'Create Product'}
          </button>
        </div>
      </form>
    </motion.div>
  )
}

export default function Products() {
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editingProduct, setEditingProduct] = useState(null)

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/products')
      setProducts(response.data)
    } catch (error) {
      toast.error('Failed to load products')
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setEditingProduct(null)
    setShowForm(true)
  }

  const handleEdit = (product) => {
    setEditingProduct(product)
    setShowForm(true)
  }

  const handleSave = async (data) => {
    try {
      if (editingProduct) {
        await api.put(`/admin/products/${editingProduct.id}`, data)
        toast.success('Product updated successfully!')
      } else {
        await api.post('/admin/products', data)
        toast.success('Product created successfully!')
      }
      
      setShowForm(false)
      setEditingProduct(null)
      loadProducts()
    } catch (error) {
      toast.error('Failed to save product')
    }
  }

  const handleToggle = async (product) => {
    try {
      await api.put(`/admin/products/${product.id}`, {
        ...product,
        is_active: !product.is_active
      })
      toast.success(`Product ${product.is_active ? 'deactivated' : 'activated'}!`)
      loadProducts()
    } catch (error) {
      toast.error('Failed to update product status')
    }
  }

  const handleDelete = async (product) => {
    if (!confirm(`Are you sure you want to delete "${product.label}"?`)) {
      return
    }

    try {
      await api.delete(`/admin/products/${product.id}`)
      toast.success('Product deleted successfully!')
      loadProducts()
    } catch (error) {
      toast.error('Failed to delete product')
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingProduct(null)
  }

  const activeProducts = products.filter(p => p.is_active)
  const inactiveProducts = products.filter(p => !p.is_active)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Products & Packages</h1>
          <p className="mt-2 text-gray-600">
            Manage your credit packages and time sessions. Changes apply immediately to your bot.
          </p>
        </div>
        
        {!showForm && (
          <button
            onClick={handleCreate}
            className="btn-primary"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Product
          </button>
        )}
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <CurrencyDollarIcon className="h-8 w-8 text-green-500" />
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Total Products</p>
              <p className="text-2xl font-semibold text-gray-900">{products.length}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <EyeIcon className="h-8 w-8 text-blue-500" />
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Active Products</p>
              <p className="text-2xl font-semibold text-gray-900">{activeProducts.length}</p>
            </div>
          </div>
        </div>

        <div className="card p-6">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <ClockIcon className="h-8 w-8 text-purple-500" />
            </div>
            <div className="ml-5">
              <p className="text-sm font-medium text-gray-500">Time Sessions</p>
              <p className="text-2xl font-semibold text-gray-900">
                {products.filter(p => p.item_type === 'time').length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Create/Edit Form */}
      {showForm && (
        <ProductForm
          product={editingProduct}
          onSave={handleSave}
          onCancel={handleCancel}
        />
      )}

      {/* Active Products */}
      {activeProducts.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Active Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {activeProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onEdit={handleEdit}
                onToggle={handleToggle}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      )}

      {/* Inactive Products */}
      {inactiveProducts.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Inactive Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {inactiveProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onEdit={handleEdit}
                onToggle={handleToggle}
                onDelete={handleDelete}
              />
            ))}
          </div>
        </div>
      )}

      {/* Empty State */}
      {products.length === 0 && !showForm && (
        <div className="text-center py-12">
          <CurrencyDollarIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No products</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by creating your first credit package.</p>
          <div className="mt-6">
            <button
              onClick={handleCreate}
              className="btn-primary"
            >
              <PlusIcon className="h-5 w-5 mr-2" />
              Create Your First Product
            </button>
          </div>
        </div>
      )}
    </div>
  )
} 