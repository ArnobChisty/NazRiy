import { useEffect, useRef, useState } from 'react'
import type { ImgHTMLAttributes, SyntheticEvent } from 'react'

type ReliableImageProps = ImgHTMLAttributes<HTMLImageElement>

const ReliableImage = ({ src = '', className = '', onLoad, onError, ...props }: ReliableImageProps) => {
  const [state, setState] = useState(() => ({ src, attempt: 0, loaded: false }))
  const retryTimer = useRef<number | undefined>(undefined)
  const current = state.src === src ? state : { src, attempt: 0, loaded: false }

  useEffect(() => {
    window.clearTimeout(retryTimer.current)
    const retryWhenOnline = () => setState({ src, attempt: 0, loaded: false })
    window.addEventListener('online', retryWhenOnline)
    return () => {
      window.clearTimeout(retryTimer.current)
      window.removeEventListener('online', retryWhenOnline)
    }
  }, [src])

  const imageLoaded = (event: SyntheticEvent<HTMLImageElement>) => {
    window.clearTimeout(retryTimer.current)
    setState({ src, attempt: current.attempt, loaded: true })
    onLoad?.(event)
  }

  const imageFailed = (event: SyntheticEvent<HTMLImageElement>) => {
    onError?.(event)
    window.clearTimeout(retryTimer.current)
    if (current.attempt >= 3) {
      retryTimer.current = window.setTimeout(() => {
        setState({ src, attempt: 0, loaded: false })
      }, 10_000)
      return
    }
    const delays = [350, 900, 1800]
    retryTimer.current = window.setTimeout(() => {
      setState({ src, attempt: current.attempt + 1, loaded: false })
    }, delays[current.attempt])
  }

  return <img {...props} key={`${src}:${current.attempt}`} src={src} className={`${className} reliable-image ${current.loaded ? 'reliable-image-ready' : 'reliable-image-loading'}`.trim()} onLoad={imageLoaded} onError={imageFailed} />
}

export default ReliableImage
