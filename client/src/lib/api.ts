export type Recipe = {
  id: string
  title: string
  cuisine: string
  type: string
  time: number | null
  kcal: number | null
  difficulty: string | null
  tags: string[]
  image: string
  missing: number
  ingredients: string[]
  measures: string[]
  description: string
  instructions: string
  source: string
  youtube: string
}

export type RecipeList = { items: Recipe[]; total: number }
export type Meta = {
  cuisines: string[]
  types: string[]
  ingredients: string[]
  difficulties: string[]
  time_options: number[]
}

const API_URL = (process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api').replace(/\/$/, '')

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, { ...init, cache: 'no-store' })
  if (!res.ok) {
    const body = await res.text().catch(() => '')
    throw new Error(body || `API error ${res.status}`)
  }
  return res.json()
}

function qs(params: Record<string, string | number | boolean | undefined>) {
  const p = new URLSearchParams()
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== '' && v !== false) p.set(k, String(v))
  })
  const value = p.toString()
  return value ? `?${value}` : ''
}

export const api = {
  recipes(params: {
    q?: string; cuisine?: string; type?: string; ingredient?: string;
    max_time?: number; diet?: string; difficulty?: string; only_pantry?: boolean;
    pantry?: string; limit?: number; offset?: number
  } = {}) {
    return request<RecipeList>(`/recipes${qs(params)}`)
  },
  recipe(id: string) { return request<Recipe>(`/recipes/${encodeURIComponent(id)}`) },
  random() { return request<Recipe>('/recipes/random') },
  meta() { return request<Meta>('/meta') },
  pantryIngredients() { return request<{ items: string[] }>('/pantry/ingredients') },
}

export { API_URL }
