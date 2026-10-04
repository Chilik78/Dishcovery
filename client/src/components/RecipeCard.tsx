'use client'
import Link from 'next/link'
import { Recipe } from '@/lib/api'

export default function RecipeCard({ recipe, saved, onSave }: { recipe: Recipe; saved: boolean; onSave: (id:string)=>void }) {
  return <article className="card">
    <Link href={`/recipe/${recipe.id}`} className="cardImage">
      {recipe.image ? <img src={recipe.image} alt={recipe.title} loading="lazy" /> : null}
      <button className="heart" aria-label={saved ? 'Убрать из сохранённых' : 'Сохранить'} onClick={(e)=>{e.preventDefault();onSave(recipe.id)}}>{saved ? '♥' : '♡'}</button>
    </Link>
    <div className="cardBody">
      <div className="meta"><span>{recipe.cuisine}</span><span>•</span><span>{recipe.type}</span>{recipe.time ? <><span>•</span><span>{recipe.time} мин</span></> : null}</div>
      <h3>{recipe.title}</h3>
      <p>{recipe.description}</p>
      {recipe.kcal != null ? <span className="tag">{recipe.kcal} ккал</span> : null}
      {recipe.difficulty ? <span className="tag">{recipe.difficulty}</span> : null}
      {recipe.missing > 0 ? <div className="missing">Не хватает: {recipe.missing}</div> : null}
    </div>
  </article>
}
