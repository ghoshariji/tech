import { describe, it, expect } from 'vitest'
import { formatCurrency, formatDate, getStatusColor, cn } from '@/lib/utils'

describe('formatCurrency', () => {
  it('formats number to USD currency', () => {
    expect(formatCurrency(1234.56)).toBe('$1,234.56')
  })
  it('handles string input', () => {
    expect(formatCurrency('99.99')).toBe('$99.99')
  })
})

describe('getStatusColor', () => {
  it('returns yellow class for PENDING', () => {
    expect(getStatusColor('PENDING')).toContain('yellow')
  })
  it('returns green class for DELIVERED', () => {
    expect(getStatusColor('DELIVERED')).toContain('green')
  })
  it('returns red class for CANCELLED', () => {
    expect(getStatusColor('CANCELLED')).toContain('red')
  })
})

describe('cn', () => {
  it('merges classes', () => {
    expect(cn('px-2', 'py-2')).toBe('px-2 py-2')
  })
  it('handles conditional classes', () => {
    expect(cn('base', false && 'hidden', 'active')).toBe('base active')
  })
})
