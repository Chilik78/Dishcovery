'use client'
import { useEffect, useMemo, useRef, useState } from 'react'
import { api, Meta, Recipe } from '@/lib/api'
import RecipeCard from './RecipeCard'

const PAGE_SIZE = 24

export default function HomeClient() {
  const [recipes,setRecipes]=useState<Recipe[]>([])
  const [meta,setMeta]=useState<Meta|null>(null)
  const [q,setQ]=useState('')
  const [search,setSearch]=useState('')
  const [cuisine,setCuisine]=useState('')
  const [type,setType]=useState('')
  const [ingredient,setIngredient]=useState('')
  const [pantry,setPantry]=useState<string[]>([])
  const [pendingPantry,setPendingPantry]=useState<string[]>([])
  const [onlyPantry,setOnlyPantry]=useState(false)
  const [saved,setSaved]=useState<string[]>([])
  const [loading,setLoading]=useState(true)
  const [loadingMore,setLoadingMore]=useState(false)
  const [error,setError]=useState('')
  const [showPantry,setShowPantry]=useState(false)
  const [total,setTotal]=useState(0)
  const [offset,setOffset]=useState(0)
  const sentinelRef=useRef<HTMLDivElement|null>(null)

  const unique = (items: string[] = []) => Array.from(new Set(items.filter(Boolean)))

  useEffect(()=>{
    const s=localStorage.getItem('dishcovery:saved'); if(s) setSaved(JSON.parse(s))
    api.meta().then(data=>setMeta({
      ...data,
      cuisines: unique(data.cuisines),
      types: unique(data.types),
      ingredients: unique(data.ingredients),
      difficulties: unique(data.difficulties),
      time_options: Array.from(new Set(data.time_options)),
    })).catch(e=>setError(e.message))
  },[])

  const load = async (nextOffset: number, append: boolean) => {
    if (append) setLoadingMore(true)
    else setLoading(true)
    setError('')
    try {
      const data=await api.recipes({
        q:search,
        cuisine:cuisine==='Все кухни'?'':cuisine,
        type,
        ingredient,
        only_pantry:onlyPantry,
        pantry:pantry.join(','),
        limit:PAGE_SIZE,
        offset:nextOffset,
      })
      setTotal(data.total)
      setOffset(nextOffset + data.items.length)
      setRecipes(prev => {
        if (!append) return data.items
        const seen = new Set(prev.map(r => r.id))
        return [...prev, ...data.items.filter(r => !seen.has(r.id))]
      })
    } catch(e) {
      setError(e instanceof Error ? e.message : 'Не удалось загрузить рецепты')
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }

  // Reset pagination whenever the active filters change.
  useEffect(()=>{
    setRecipes([])
    setOffset(0)
    setTotal(0)
    load(0, false)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[search,cuisine,type,ingredient,onlyPantry,pantry])

  const hasMore = recipes.length < total

  // Infinite scroll: fetch the next page when the sentinel approaches the viewport.
  useEffect(()=>{
    const node=sentinelRef.current
    if (!node || loading || loadingMore || !hasMore) return
    const observer=new IntersectionObserver(entries=>{
      if (entries[0]?.isIntersecting && !loadingMore) load(offset, true)
    }, { rootMargin: '600px 0px' })
    observer.observe(node)
    return ()=>observer.disconnect()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  },[offset,loading,loadingMore,hasMore,search,cuisine,type,ingredient,onlyPantry,pantry])

  const save = (id:string) => {
    const next=saved.includes(id)?saved.filter(x=>x!==id):[...saved,id]
    setSaved(next); localStorage.setItem('dishcovery:saved',JSON.stringify(next))
  }
  const ingredientOptions=useMemo(()=>unique(meta?.ingredients).slice(0,120),[meta])
  const cuisineOptions=useMemo(()=>unique(meta?.cuisines),[meta])
  const typeOptions=useMemo(()=>unique(meta?.types),[meta])

  return <main className="shell">
    <header className="topbar"><div className="brand">Dish<span>covery</span></div><nav className="nav"><a className="active" href="#recipes">Рецепты</a><a href="#saved">Сохранённые</a><button className={onlyPantry?'active':''} onClick={()=>setOnlyPantry(v=>!v)}>Из того, что есть</button></nav></header>
    <section className="hero">
      <div className="heroCard"><div className="eyebrow">Ваш персональный поиск еды</div><h1>Что приготовим сегодня?</h1><p>Ищите реальные рецепты по названию, кухне, типу блюда и ингредиентам. Состав рецептов загружается с Dishcovery API.</p><form className="search" onSubmit={e=>{e.preventDefault();setSearch(q.trim())}}><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Например, pasta, chicken, curry…"/><button>Найти</button></form></div>
      <div className="sideCard"><div><div className="eyebrow" style={{color:'#56631f'}}>Панtry mode</div><h2>Приготовьте из того, что уже есть дома.</h2><p>Выберите ингредиенты, и сервер найдёт блюда с минимальным количеством недостающих продуктов.</p></div><button className="primary" onClick={()=>{setShowPantry(v=>!v);setPendingPantry(pantry)}}>{showPantry?'Скрыть':'Выбрать продукты'}</button></div>
    </section>

    {showPantry && <section className="pantry"><strong>Что есть дома?</strong><div className="checklist">{ingredientOptions.map(i=><button key={i} className={`check ${pendingPantry.includes(i)?'on':''}`} onClick={()=>setPendingPantry(p=>p.includes(i)?p.filter(x=>x!==i):[...p,i])}>{i}</button>)}</div><div style={{marginTop:14,display:'flex',gap:8,flexWrap:'wrap'}}><button className="primary" onClick={()=>{setPantry(pendingPantry);setOnlyPantry(false)}} disabled={!pendingPantry.length}>Применить ингредиенты</button>{pendingPantry.length>0&&<button className="primary" onClick={()=>{setPantry(pendingPantry);setOnlyPantry(true)}}>Показать только доступные</button>}<button className="pill" onClick={()=>{setPendingPantry([]);setPantry([]);setOnlyPantry(false)}}>Очистить</button></div></section>}

    <div className="filterBar">
      {cuisineOptions.map(c=><button key={c} className={`pill ${cuisine===(c==='Все кухни'?'':c)?'selected':''}`} onClick={()=>setCuisine(c==='Все кухни'?'':c)}>{c}</button>)}
    </div>
    <div className="toolbar"><div className="muted">{loading?'Загружаем…':`${recipes.length}${total ? ` из ${total}` : ''} рецептов`}</div><div style={{display:'flex',gap:8}}><select className="select" value={type} onChange={e=>setType(e.target.value)}><option value="">Все типы</option>{typeOptions.map(t=><option key={t}>{t}</option>)}</select><select className="select" value={ingredient} onChange={e=>setIngredient(e.target.value)}><option value="">Любой ингредиент</option>{ingredientOptions.map(i=><option key={i}>{i}</option>)}</select></div></div>
    <div id="recipes" className="sectionHead"><h2>Рецепты для вас</h2><span className="muted">Данные из API</span></div>
    {error?<div className="error">{error}<br/><small>Проверьте, что FastAPI запущен на {process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api'}.</small></div>:loading?<div className="loading">Загружаем рецепты…</div>:recipes.length===0?<div className="empty">Ничего не найдено. Попробуйте изменить запрос или фильтры.</div>:<>
      <div className="grid">{recipes.map(r=><RecipeCard key={r.id} recipe={r} saved={saved.includes(r.id)} onSave={save}/>)}</div>
      <div ref={sentinelRef} style={{height:1}} aria-hidden="true" />
      {loadingMore && <div className="loading">Загружаем ещё рецепты…</div>}
      {!loadingMore && !hasMore && <div className="muted" style={{textAlign:'center',padding:'24px 0'}}>Вы посмотрели все доступные рецепты.</div>}
    </>}
  </main>
}
