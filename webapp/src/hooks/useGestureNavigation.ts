import { useCallback, useEffect, useRef, useState } from 'react'
import { useTelegramWebApp } from './useTelegramWebApp'

interface SwipeGesture {
  startX: number
  startY: number
  endX: number
  endY: number
  deltaX: number
  deltaY: number
  direction: 'left' | 'right' | 'up' | 'down' | 'none'
  distance: number
  velocity: number
  timestamp: number
}

interface GestureConfig {
  threshold: number
  velocityThreshold: number
  preventScroll: boolean
  enableHapticFeedback: boolean
  debounceTime: number
}

const defaultConfig: GestureConfig = {
  threshold: 50,
  velocityThreshold: 0.3,
  preventScroll: false,
  enableHapticFeedback: true,
  debounceTime: 300
}

type SwipeHandler = (gesture: SwipeGesture) => void

export const useGestureNavigation = (
  config: Partial<GestureConfig> = {},
  onSwipeLeft?: SwipeHandler,
  onSwipeRight?: SwipeHandler,
  onSwipeUp?: SwipeHandler,
  onSwipeDown?: SwipeHandler
) => {
  const mergedConfig = { ...defaultConfig, ...config }
  const { hapticFeedback, hasHapticFeedback, isMobile } = useTelegramWebApp()
  
  const [isEnabled, setIsEnabled] = useState(true)
  const [isGesturing, setIsGesturing] = useState(false)
  const [currentGesture, setCurrentGesture] = useState<SwipeGesture | null>(null)
  
  const touchStartRef = useRef<{ x: number; y: number; timestamp: number } | null>(null)
  const lastGestureRef = useRef<number>(0)
  const elementRef = useRef<HTMLElement | null>(null)

  // Calculate gesture details
  const calculateGesture = useCallback((
    startX: number,
    startY: number,
    endX: number,
    endY: number,
    startTime: number,
    endTime: number
  ): SwipeGesture => {
    const deltaX = endX - startX
    const deltaY = endY - startY
    const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
    const duration = endTime - startTime
    const velocity = distance / duration

    let direction: SwipeGesture['direction'] = 'none'
    
    if (Math.abs(deltaX) > Math.abs(deltaY)) {
      // Horizontal swipe
      if (Math.abs(deltaX) > mergedConfig.threshold) {
        direction = deltaX > 0 ? 'right' : 'left'
      }
    } else {
      // Vertical swipe
      if (Math.abs(deltaY) > mergedConfig.threshold) {
        direction = deltaY > 0 ? 'down' : 'up'
      }
    }

    return {
      startX,
      startY,
      endX,
      endY,
      deltaX,
      deltaY,
      direction,
      distance,
      velocity,
      timestamp: endTime
    }
  }, [mergedConfig.threshold])

  // Handle touch start
  const handleTouchStart = useCallback((event: TouchEvent) => {
    if (!isEnabled || !isMobile) return

    const touch = event.touches[0]
    touchStartRef.current = {
      x: touch.clientX,
      y: touch.clientY,
      timestamp: Date.now()
    }

    setIsGesturing(true)

    // Haptic feedback for gesture start
    if (mergedConfig.enableHapticFeedback && hasHapticFeedback) {
      hapticFeedback.selection()
    }
  }, [isEnabled, isMobile, mergedConfig.enableHapticFeedback, hasHapticFeedback, hapticFeedback])

  // Handle touch move
  const handleTouchMove = useCallback((event: TouchEvent) => {
    if (!isEnabled || !touchStartRef.current || !isMobile) return

    const touch = event.touches[0]
    const startTouch = touchStartRef.current
    
    const gesture = calculateGesture(
      startTouch.x,
      startTouch.y,
      touch.clientX,
      touch.clientY,
      startTouch.timestamp,
      Date.now()
    )

    setCurrentGesture(gesture)

    // Prevent scroll if configured and gesture is horizontal
    if (mergedConfig.preventScroll && ['left', 'right'].includes(gesture.direction)) {
      event.preventDefault()
    }
  }, [isEnabled, isMobile, calculateGesture, mergedConfig.preventScroll])

  // Handle touch end
  const handleTouchEnd = useCallback((event: TouchEvent) => {
    if (!isEnabled || !touchStartRef.current || !isMobile) return

    const touch = event.changedTouches[0]
    const startTouch = touchStartRef.current
    const endTime = Date.now()

    // Debounce gestures
    if (endTime - lastGestureRef.current < mergedConfig.debounceTime) {
      setIsGesturing(false)
      touchStartRef.current = null
      return
    }

    const gesture = calculateGesture(
      startTouch.x,
      startTouch.y,
      touch.clientX,
      touch.clientY,
      startTouch.timestamp,
      endTime
    )

    // Check if gesture meets velocity and distance thresholds
    const isValidGesture = 
      gesture.distance > mergedConfig.threshold && 
      gesture.velocity > mergedConfig.velocityThreshold

    if (isValidGesture) {
      // Haptic feedback for successful gesture
      if (mergedConfig.enableHapticFeedback && hasHapticFeedback) {
        hapticFeedback.impact('light')
      }

      // Call appropriate handler
      switch (gesture.direction) {
        case 'left':
          onSwipeLeft?.(gesture)
          break
        case 'right':
          onSwipeRight?.(gesture)
          break
        case 'up':
          onSwipeUp?.(gesture)
          break
        case 'down':
          onSwipeDown?.(gesture)
          break
      }

      lastGestureRef.current = endTime
    }

    setIsGesturing(false)
    setCurrentGesture(null)
    touchStartRef.current = null
  }, [
    isEnabled,
    isMobile,
    calculateGesture,
    mergedConfig.threshold,
    mergedConfig.velocityThreshold,
    mergedConfig.debounceTime,
    mergedConfig.enableHapticFeedback,
    hasHapticFeedback,
    hapticFeedback,
    onSwipeLeft,
    onSwipeRight,
    onSwipeUp,
    onSwipeDown
  ])

  // Attach event listeners to element
  const attachGestures = useCallback((element: HTMLElement | null) => {
    if (elementRef.current) {
      // Remove old listeners
      elementRef.current.removeEventListener('touchstart', handleTouchStart)
      elementRef.current.removeEventListener('touchmove', handleTouchMove)
      elementRef.current.removeEventListener('touchend', handleTouchEnd)
    }

    elementRef.current = element

    if (element && isMobile) {
      // Add new listeners
      element.addEventListener('touchstart', handleTouchStart, { passive: false })
      element.addEventListener('touchmove', handleTouchMove, { passive: false })
      element.addEventListener('touchend', handleTouchEnd, { passive: true })
    }
  }, [handleTouchStart, handleTouchMove, handleTouchEnd, isMobile])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (elementRef.current) {
        elementRef.current.removeEventListener('touchstart', handleTouchStart)
        elementRef.current.removeEventListener('touchmove', handleTouchMove)
        elementRef.current.removeEventListener('touchend', handleTouchEnd)
      }
    }
  }, [handleTouchStart, handleTouchMove, handleTouchEnd])

  // Auto-attach to document body if no specific element is provided
  useEffect(() => {
    if (!elementRef.current && isMobile) {
      attachGestures(document.body)
    }
  }, [attachGestures, isMobile])

  // Gesture direction indicators
  const getGestureIndicator = () => {
    if (!isGesturing || !currentGesture) return null

    const { direction, distance, velocity } = currentGesture
    const progress = Math.min(distance / (mergedConfig.threshold * 2), 1)

    return {
      direction,
      progress,
      velocity,
      isValid: distance > mergedConfig.threshold && velocity > mergedConfig.velocityThreshold
    }
  }

  return {
    // State
    isEnabled,
    isGesturing,
    currentGesture,
    gestureIndicator: getGestureIndicator(),
    
    // Controls
    enable: () => setIsEnabled(true),
    disable: () => setIsEnabled(false),
    attachGestures,
    
    // Config
    config: mergedConfig,
    
    // Device info
    isMobileDevice: isMobile,
    hasHaptic: hasHapticFeedback
  }
}

// Hook for page navigation gestures
export const usePageNavigation = (
  pages: string[],
  currentPage: string,
  onNavigate: (page: string) => void,
  config?: Partial<GestureConfig>
) => {
  const currentIndex = pages.indexOf(currentPage)
  
  const handleSwipeLeft = useCallback(() => {
    // Go to next page
    if (currentIndex < pages.length - 1) {
      onNavigate(pages[currentIndex + 1])
    }
  }, [currentIndex, pages, onNavigate])

  const handleSwipeRight = useCallback(() => {
    // Go to previous page
    if (currentIndex > 0) {
      onNavigate(pages[currentIndex - 1])
    }
  }, [currentIndex, pages, onNavigate])

  const gestureNavigation = useGestureNavigation(
    {
      threshold: 100,
      velocityThreshold: 0.5,
      preventScroll: true,
      ...config
    },
    handleSwipeLeft,
    handleSwipeRight
  )

  return {
    ...gestureNavigation,
    canSwipeLeft: currentIndex < pages.length - 1,
    canSwipeRight: currentIndex > 0,
    currentPageIndex: currentIndex,
    totalPages: pages.length
  }
}

export default useGestureNavigation 