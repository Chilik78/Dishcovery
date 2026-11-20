'use client'

import { useState } from 'react'
import { api } from '@/lib/api'

export default function RecipeSteps({ recipeId }: { recipeId: string }) {
  const [steps, setSteps] = useState<string[]>([])
  const [visible, setVisible] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(false)

  async function showSteps() {
    if (steps.length > 0) {
      setVisible(!visible)
      return
    }

    setLoading(true)
    setError(false)
    try {
      const result = await api.recipeSteps(recipeId)
      setSteps(result.steps)
      setVisible(true)
    } catch {
      setError(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ marginBottom: 16 }}>
      <button
        type="button"
        className="primary"
        onClick={showSteps}
        disabled={loading}
        aria-expanded={visible}
      >
        {visible ? 'Скрыть шаги' : 'Показать по шагам'}
      </button>
      <div role="status">
        {loading && <p className="muted">Готовим пошаговую инструкцию…</p>}
        {error && <p className="notice">Не удалось сформировать шаги. Попробуйте ещё раз.</p>}
      </div>
      {visible && (
        <>
          <h3>Пошаговая инструкция с ИИ</h3>
          <ol className="instructions">
            {steps.map((step, index) => <li key={index}>{step}</li>)}
          </ol>
        </>
      )}
    </div>
  )
}
