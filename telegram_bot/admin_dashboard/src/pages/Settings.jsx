import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useForm } from 'react-hook-form'
import toast from 'react-hot-toast'
import {
  ChatBubbleLeftRightIcon,
  CurrencyDollarIcon,
  BellIcon,
  CogIcon,
  PhotoIcon,
  ClockIcon,
} from '@heroicons/react/24/outline'
import { api } from '../services/api'

const SettingsSection = ({ title, icon: Icon, children }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="card p-6"
  >
    <div className="flex items-center space-x-3 mb-6">
      <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary-100">
        <Icon className="h-6 w-6 text-primary-600" />
      </div>
      <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
    </div>
    {children}
  </motion.div>
)

export default function Settings() {
  const [loading, setLoading] = useState(false)
  const [settings, setSettings] = useState({})
  
  const { register, handleSubmit, setValue, watch, formState: { errors } } = useForm()

  // Load current settings
  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      const response = await api.get('/admin/settings')
      setSettings(response.data)
      
      // Populate form with current values
      Object.keys(response.data).forEach(key => {
        setValue(key, response.data[key])
      })
    } catch (error) {
      toast.error('Failed to load settings')
    } finally {
      setLoading(false)
    }
  }

  const updateSetting = async (key, value) => {
    try {
      await api.put('/admin/settings', { [key]: value })
      setSettings(prev => ({ ...prev, [key]: value }))
      toast.success('Setting updated successfully!')
    } catch (error) {
      toast.error('Failed to update setting')
    }
  }

  const onSubmit = async (data) => {
    try {
      setLoading(true)
      await api.put('/admin/settings/bulk', data)
      setSettings(data)
      toast.success('All settings updated successfully!')
    } catch (error) {
      toast.error('Failed to update settings')
    } finally {
      setLoading(false)
    }
  }

  if (loading && Object.keys(settings).length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Bot Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure your bot's behavior, messages, and pricing from this dashboard.
          Changes are applied immediately to your live bot.
        </p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Welcome & Messages */}
        <SettingsSection title="Welcome & Messages" icon={ChatBubbleLeftRightIcon}>
          <div className="space-y-6">
            <div>
              <label className="label">Welcome Message</label>
              <textarea
                {...register('welcome_message', { required: 'Welcome message is required' })}
                className="textarea"
                rows={4}
                placeholder="Enter the welcome message shown to new users..."
              />
              {errors.welcome_message && (
                <p className="mt-1 text-sm text-red-600">{errors.welcome_message.message}</p>
              )}
              <p className="mt-1 text-sm text-gray-500">
                This message appears when users first start the bot. Markdown formatting supported.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Low Balance Warning Message</label>
                <textarea
                  {...register('low_balance_message')}
                  className="textarea"
                  rows={3}
                  placeholder="You're running low on credits..."
                />
                <p className="mt-1 text-sm text-gray-500">
                  Shown when user credits fall below threshold.
                </p>
              </div>

              <div>
                <label className="label">Insufficient Credits Message</label>
                <textarea
                  {...register('insufficient_credits_message')}
                  className="textarea"
                  rows={3}
                  placeholder="You don't have enough credits..."
                />
                <p className="mt-1 text-sm text-gray-500">
                  Shown when user tries to send without enough credits.
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Payment Success Message</label>
                <textarea
                  {...register('payment_success_message')}
                  className="textarea"
                  rows={3}
                  placeholder="Payment successful! Credits added..."
                />
              </div>

              <div>
                <label className="label">Support Contact Message</label>
                <textarea
                  {...register('support_message')}
                  className="textarea"
                  rows={3}
                  placeholder="Our support team will respond shortly..."
                />
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* Pricing & Credits */}
        <SettingsSection title="Pricing & Credits" icon={CurrencyDollarIcon}>
          <div className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <label className="label">Text Message Cost</label>
                <input
                  {...register('cost_text_message', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="1"
                />
                <p className="mt-1 text-xs text-gray-500">Credits per text</p>
              </div>

              <div>
                <label className="label">Photo Message Cost</label>
                <input
                  {...register('cost_photo_message', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="2"
                />
                <p className="mt-1 text-xs text-gray-500">Credits per photo</p>
              </div>

              <div>
                <label className="label">Video Message Cost</label>
                <input
                  {...register('cost_video_message', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="3"
                />
                <p className="mt-1 text-xs text-gray-500">Credits per video</p>
              </div>

              <div>
                <label className="label">Document Cost</label>
                <input
                  {...register('cost_document_message', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="2"
                />
                <p className="mt-1 text-xs text-gray-500">Credits per document</p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <label className="label">New User Bonus Credits</label>
                <input
                  {...register('starting_credits', { required: true, min: 0 })}
                  type="number"
                  className="input"
                  placeholder="5"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Free credits given to new users
                </p>
              </div>

              <div>
                <label className="label">Low Balance Threshold</label>
                <input
                  {...register('low_credit_threshold', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="5"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Warning threshold for low credits
                </p>
              </div>

              <div>
                <label className="label">VIP Tier Threshold</label>
                <input
                  {...register('vip_threshold', { required: true, min: 1 })}
                  type="number"
                  className="input"
                  placeholder="100"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Credits needed for VIP status
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Regular Tier Discount (%)</label>
                <input
                  {...register('regular_discount', { required: true, min: 0, max: 50 })}
                  type="number"
                  className="input"
                  placeholder="10"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Discount percentage for regular users
                </p>
              </div>

              <div>
                <label className="label">VIP Tier Discount (%)</label>
                <input
                  {...register('vip_discount', { required: true, min: 0, max: 50 })}
                  type="number"
                  className="input"
                  placeholder="20"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Discount percentage for VIP users
                </p>
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* Notifications & Automation */}
        <SettingsSection title="Notifications & Automation" icon={BellIcon}>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Auto-Recharge Enabled</label>
                <select {...register('auto_recharge_enabled')} className="input">
                  <option value="true">Enabled</option>
                  <option value="false">Disabled</option>
                </select>
                <p className="mt-1 text-sm text-gray-500">
                  Allow users to set up automatic credit top-ups
                </p>
              </div>

              <div>
                <label className="label">Admin Notification Email</label>
                <input
                  {...register('admin_email')}
                  type="email"
                  className="input"
                  placeholder="admin@example.com"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Email for important notifications
                </p>
              </div>
            </div>

            <div>
              <label className="label">Daily Summary Enabled</label>
              <div className="mt-2 space-y-2">
                <label className="flex items-center">
                  <input
                    {...register('daily_summary')}
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Send daily summary of bot activity
                  </span>
                </label>
              </div>
            </div>
          </div>
        </SettingsSection>

        {/* Advanced Settings */}
        <SettingsSection title="Advanced Settings" icon={CogIcon}>
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="label">Maximum File Size (MB)</label>
                <input
                  {...register('max_file_size', { required: true, min: 1, max: 50 })}
                  type="number"
                  className="input"
                  placeholder="20"
                />
                <p className="mt-1 text-sm text-gray-500">
                  Maximum file size for uploads
                </p>
              </div>

              <div>
                <label className="label">Session Timeout (minutes)</label>
                <input
                  {...register('session_timeout', { required: true, min: 5 })}
                  type="number"
                  className="input"
                  placeholder="30"
                />
                <p className="mt-1 text-sm text-gray-500">
                  User session timeout duration
                </p>
              </div>
            </div>

            <div>
              <label className="label">Maintenance Mode</label>
              <div className="mt-2 space-y-2">
                <label className="flex items-center">
                  <input
                    {...register('maintenance_mode')}
                    type="checkbox"
                    className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Enable maintenance mode (blocks new messages)
                  </span>
                </label>
              </div>
            </div>

            <div>
              <label className="label">Maintenance Message</label>
              <textarea
                {...register('maintenance_message')}
                className="textarea"
                rows={3}
                placeholder="The bot is currently under maintenance..."
              />
              <p className="mt-1 text-sm text-gray-500">
                Message shown when maintenance mode is active
              </p>
            </div>
          </div>
        </SettingsSection>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
          >
            {loading ? 'Saving...' : 'Save All Settings'}
          </button>
        </div>
      </form>
    </div>
  )
} 