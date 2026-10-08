'use client'
import Link from 'next/link'
import { useEffect, useState } from 'react'
import { api, Recipe } from '@/lib/api'

export default function RecipePage({params}:{params:Promise<{id:string}>}){
  const [recipe,setRecipe]=useState<Recipe|null>(null); const [error,setError]=useState(''); const [loading,setLoading]=useState(true)
  useEffect(()=>{params.then(({id})=>api.recipe(id).then(setRecipe).catch(e=>setError(e.message)).finally(()=>setLoading(false)))},[params])
  if(loading)return <main className="shell"><div className="loading">Загружаем рецепт…</div></main>
  if(error||!recipe)return <main className="shell"><Link className="back" href="/">← Все рецепты</Link><div className="error">{error||'Рецепт не найден'}</div></main>
  return <main className="shell"><Link className="back" href="/">← Все рецепты</Link><div className="detail"><div>{recipe.image&&<img className="detailImage" src={recipe.image} alt={recipe.title}/>}</div><div><div className="meta"><span>{recipe.cuisine}</span><span>•</span><span>{recipe.type}</span></div><h1>{recipe.title}</h1><p className="muted" style={{fontSize:17,lineHeight:1.6}}>{recipe.description}</p><div className="meta" style={{fontSize:14,marginTop:14}}>{recipe.time&&<span>⏱ {recipe.time} мин</span>}{recipe.kcal!=null&&<span>🔥 {recipe.kcal} ккал</span>}{recipe.difficulty&&<span>◌ {recipe.difficulty}</span>}</div>{recipe.youtube&&<a className="notice" style={{display:'block',textDecoration:'none'}} href={recipe.youtube} target="_blank" rel="noreferrer">Видео приготовления ↗</a>}</div></div><section className="detailPanel"><h2>Ингредиенты</h2><div className="ingredients">{recipe.ingredients.map((name,i)=><div className="ingredient" key={`${name}-${i}`}><span>{name}</span><strong>{recipe.measures[i]||'по вкусу'}</strong></div>)}</div></section><section className="detailPanel"><h2>Приготовление</h2><div className="instructions">{recipe.instructions||'Инструкция не предоставлена API.'}</div></section></main>
}
