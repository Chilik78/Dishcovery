import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Dishcovery',
  description: 'Рецепты из того, что есть дома',
}

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ru"><body>{children}</body></html>
}
