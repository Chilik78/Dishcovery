import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  ArrowLeft, ArrowRight, Bookmark, Check, ChevronDown, Clock3, Flame,
  Heart, Home, Leaf, Menu, Minus, Play, Plus, Search, ShoppingBasket,
  Sparkles, SlidersHorizontal, Timer, UtensilsCrossed, X, Zap
} from 'lucide-react';
import './styles.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const recipes = [
  { id:1, title:'Паста с томатами и бурратой', cuisine:'Итальянская', type:'Ужин', time:20, kcal:520, difficulty:'Новичок', tags:['Вегетарианское','Быстро'], image:'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?auto=format&fit=crop&w=900&q=85', missing:0, ingredients:['Паста','Томаты','Буррата','Базилик','Чеснок'], description:'Нежная паста с запечёнными томатами, кремовой бурратой и свежим базиликом.' },
  { id:2, title:'Боул с лососем и авокадо', cuisine:'Азиатская', type:'Ужин', time:25, kcal:610, difficulty:'Уверенный', tags:['Высокий белок','Без глютена'], image:'https://images.unsplash.com/photo-1547592180-85f173990554?auto=format&fit=crop&w=900&q=85', missing:1, ingredients:['Лосось','Авокадо','Рис','Огурец','Эдамаме','Соевый соус'], description:'Свежий и сытный боул с лососем, хрустящими овощами и рисом.' },
  { id:3, title:'Крем-суп из тыквы', cuisine:'Европейская', type:'Суп', time:35, kcal:290, difficulty:'Новичок', tags:['Веган','Уютная еда'], image:'https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a?auto=format&fit=crop&w=900&q=85', missing:2, ingredients:['Тыква','Лук','Морковь','Кокосовое молоко','Имбирь'], description:'Шёлковистый крем-суп с кокосовым молоком и тёплой ноткой имбиря.' },
  { id:4, title:'Шакшука с фетой', cuisine:'Ближневосточная', type:'Завтрак', time:18, kcal:430, difficulty:'Новичок', tags:['Белок','Одна сковорода'], image:'https://images.unsplash.com/photo-1590412200988-a436970781fa?auto=format&fit=crop&w=900&q=85', missing:0, ingredients:['Яйца','Томаты','Фета','Перец','Лук','Зелень'], description:'Яйца, томаты и фета — всё в одной сковороде и за считанные минуты.' },
  { id:5, title:'Хрустящий цыплёнок с салатом', cuisine:'Средиземноморская', type:'Ужин', time:30, kcal:570, difficulty:'Уверенный', tags:['Высокий белок'], image:'https://images.unsplash.com/photo-1532550907401-a500c9a57435?auto=format&fit=crop&w=900&q=85', missing:1, ingredients:['Куриное филе','Микс салата','Лимон','Пармезан','Панко'], description:'Золотистый цыплёнок с лимонным салатом и хрустящей корочкой.' },
  { id:6, title:'Шоколадный мусс за 10 минут', cuisine:'Французская', type:'Десерт', time:10, kcal:340, difficulty:'Новичок', tags:['10 минут','Десерт'], image:'https://images.unsplash.com/photo-1578985545062-69928b1d9587?auto=format&fit=crop&w=900&q=85', missing:1, ingredients:['Шоколад','Сливки','Какао','Ягоды'], description:'Воздушный шоколадный десерт, когда хочется сладкого прямо сейчас.' }
];

const pantryDefault = ['Яйца','Томаты','Чеснок','Паста','Авокадо'];

function App() {
  const [query, setQuery] = useState('');
  const [activeTab, setActiveTab] = useState('Для вас');
  const [pantry, setPantry] = useState(pantryDefault);
  const [selectedCuisine, setSelectedCuisine] = useState('Все кухни');
  const [maxTime, setMaxTime] = useState(60);
  const [diet, setDiet] = useState('Все');
  const [difficulty, setDifficulty] = useState('Любая');
  const [onlyPantry, setOnlyPantry] = useState(false);
  const [selected, setSelected] = useState(null);
  const [saved, setSaved] = useState([]);
  const [showFilters, setShowFilters] = useState(false);
  const [showPantry, setShowPantry] = useState(false);
  const [mobileNav, setMobileNav] = useState(false);

  const filtered = useMemo(() => recipes.filter(r => {
    const q = query.toLowerCase();
    const textMatch = !q || [r.title, r.cuisine, r.type, ...r.ingredients].join(' ').toLowerCase().includes(q);
    const cuisineMatch = selectedCuisine === 'Все кухни' || r.cuisine === selectedCuisine;
    const timeMatch = r.time <= maxTime;
    const dietMatch = diet === 'Все' || r.tags.some(t => t.toLowerCase().includes(diet.toLowerCase()));
    const difficultyMatch = difficulty === 'Любая' || r.difficulty === difficulty;
    const pantryMatch = !onlyPantry || r.missing === 0;
    return textMatch && cuisineMatch && timeMatch && dietMatch && difficultyMatch && pantryMatch;
  }), [query, selectedCuisine, maxTime, diet, difficulty, onlyPantry]);

  const togglePantry = (item) => setPantry(p => p.includes(item) ? p.filter(x => x !== item) : [...p, item]);
  const toggleSave = (id) => setSaved(s => s.includes(id) ? s.filter(x => x !== id) : [...s, id]);

  if (selected) return <RecipeDetail recipe={selected} onBack={() => setSelected(null)} saved={saved.includes(selected.id)} onSave={() => toggleSave(selected.id)} />;

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand"><div className="brand-mark"><UtensilsCrossed size={19}/></div><span>dish<span>covery</span></span></div>
        <nav className="desktop-nav">
          {['Для вас','Рецепты','Сохранённые'].map(t => <button key={t} className={activeTab===t?'active':''} onClick={()=>setActiveTab(t)}>{t}</button>)}
        </nav>
        <div className="top-actions">
          <button className="icon-btn mobile-only" onClick={()=>setMobileNav(!mobileNav)}><Menu size={20}/></button>
          <button className="profile">А</button>
        </div>
      </header>

      {mobileNav && <div className="mobile-nav">{['Для вас','Рецепты','Сохранённые'].map(t => <button key={t} onClick={()=>{setActiveTab(t);setMobileNav(false)}}>{t}</button>)}</div>}

      <main>
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow"><Sparkles size={15}/> Персональный подбор</div>
            <h1>Что приготовим<br/><em>сегодня?</em></h1>
            <p>Расскажи, что есть под рукой, сколько времени и чего хочется — мы найдём идеальный рецепт.</p>
          </div>
          <div className="search-wrap">
            <Search size={20}/>
            <input value={query} onChange={e=>setQuery(e.target.value)} placeholder="Например, паста, курица или авокадо…" />
            {query && <button className="clear" onClick={()=>setQuery('')}><X size={16}/></button>}
            <button className="filter-trigger" onClick={()=>setShowFilters(!showFilters)}><SlidersHorizontal size={18}/><span>Фильтры</span></button>
          </div>
        </section>

        <section className="pantry-card">
          <div className="pantry-main">
            <div className="pantry-icon"><ShoppingBasket size={21}/></div>
            <div><strong>Что есть в холодильнике?</strong><span>Подберём блюда из того, что уже есть дома.</span></div>
          </div>
          <div className="pantry-chips">
            {pantry.slice(0,4).map(i=><button key={i} className="ingredient-chip" onClick={()=>togglePantry(i)}>{i}<X size={13}/></button>)}
            <button className="add-chip" onClick={()=>setShowPantry(true)}><Plus size={15}/> Добавить</button>
          </div>
          <button className={`ready-toggle ${onlyPantry?'on':''}`} onClick={()=>setOnlyPantry(!onlyPantry)}><span></span>Готово прямо сейчас</button>
        </section>

        {showFilters && <FilterPanel {...{selectedCuisine,setSelectedCuisine,maxTime,setMaxTime,diet,setDiet,difficulty,setDifficulty}} />}

        <section className="section-head">
          <div><div className="eyebrow"><Zap size={14}/> Подобрано для вас</div><h2>{onlyPantry ? 'Можно приготовить сейчас' : 'Идеи на сегодня'}</h2></div>
          <button className="link-btn" onClick={()=>{setSelectedCuisine('Все кухни');setMaxTime(60);setDiet('Все');setDifficulty('Любая');setOnlyPantry(false);setQuery('')}}>Сбросить фильтры <ArrowRight size={16}/></button>
        </section>

        <div className="quick-filters">
          {['Все кухни','Итальянская','Азиатская','Ближневосточная','Европейская'].map(c=><button className={selectedCuisine===c?'selected':''} onClick={()=>setSelectedCuisine(c)} key={c}>{c}</button>)}
          <span className="divider"></span>
          {[15,30,60].map(t=><button className={maxTime===t?'selected':''} onClick={()=>setMaxTime(t)} key={t}><Clock3 size={14}/> до {t} мин</button>)}
        </div>

        <section className="recipe-grid">
          {filtered.map(r=><RecipeCard key={r.id} recipe={r} saved={saved.includes(r.id)} onSave={()=>toggleSave(r.id)} onOpen={()=>setSelected(r)} />)}
          {!filtered.length && <div className="empty"><div className="empty-icon"><Search/></div><h3>Ничего не нашли</h3><p>Попробуйте убрать часть фильтров или поискать другой ингредиент.</p></div>}
        </section>
      </main>

      {showPantry && <PantryModal pantry={pantry} toggle={togglePantry} onClose={()=>setShowPantry(false)} />}
      <footer><span>dishcovery</span><span>Открой своё следующее любимое блюдо.</span><span>© 2026</span></footer>
    </div>
  );
}

function FilterPanel({selectedCuisine,setSelectedCuisine,maxTime,setMaxTime,diet,setDiet,difficulty,setDifficulty}) {
  return <div className="filter-panel">
    <FilterGroup title="Кухня"><select value={selectedCuisine} onChange={e=>setSelectedCuisine(e.target.value)}>{['Все кухни','Итальянская','Азиатская','Ближневосточная','Европейская'].map(x=><option key={x}>{x}</option>)}</select></FilterGroup>
    <FilterGroup title="Время"><div className="segmented">{[15,30,60].map(x=><button className={maxTime===x?'selected':''} onClick={()=>setMaxTime(x)} key={x}>{x} мин</button>)}</div></FilterGroup>
    <FilterGroup title="Диета"><div className="segmented wrap">{['Все','Веган','Кето','Без глютена'].map(x=><button className={diet===x?'selected':''} onClick={()=>setDiet(x)} key={x}>{x}</button>)}</div></FilterGroup>
    <FilterGroup title="Сложность"><div className="segmented">{['Любая','Новичок','Уверенный'].map(x=><button className={difficulty===x?'selected':''} onClick={()=>setDifficulty(x)} key={x}>{x}</button>)}</div></FilterGroup>
  </div>
}
function FilterGroup({title,children}) { return <div className="filter-group"><label>{title}</label>{children}</div> }

function RecipeCard({recipe,saved,onSave,onOpen}) {
  return <article className="recipe-card" onClick={onOpen}>
    <div className="card-image"><img src={recipe.image} alt={recipe.title}/><div className="image-gradient"></div><div className="card-top"><span className="time-pill"><Clock3 size={13}/>{recipe.time} мин</span><button className={`save-btn ${saved?'saved':''}`} onClick={e=>{e.stopPropagation();onSave()}}>{saved?<Heart size={17} fill="currentColor"/>:<Bookmark size={17}/>}</button></div>{recipe.missing>0 && <span className="missing-badge">Не хватает: {recipe.missing}</span>}</div>
    <div className="card-body"><div className="card-meta"><span>{recipe.cuisine}</span><span>•</span><span>{recipe.difficulty}</span></div><h3>{recipe.title}</h3><p>{recipe.description}</p><div className="card-bottom"><span><Flame size={14}/>{recipe.kcal} ккал</span><span className="tags">{recipe.tags.slice(0,1).map(t=><b key={t}>{t}</b>)}</span></div></div>
  </article>
}

function PantryModal({pantry,toggle,onClose}) {
  const items=['Яйца','Томаты','Чеснок','Паста','Авокадо','Лук','Рис','Курица','Лосось','Картофель','Морковь','Сыр','Молоко','Базилик'];
  return <div className="modal-backdrop" onClick={onClose}><div className="modal" onClick={e=>e.stopPropagation()}><div className="modal-head"><div><div className="eyebrow"><ShoppingBasket size={14}/> Моя кладовая</div><h2>Что есть дома?</h2></div><button className="icon-btn" onClick={onClose}><X/></button></div><p className="modal-sub">Отметь продукты, которые сейчас есть. Мы учтём их при подборе.</p><div className="ingredient-grid">{items.map(i=><button className={pantry.includes(i)?'picked':''} key={i} onClick={()=>toggle(i)}>{pantry.includes(i)?<Check size={15}/>:<Plus size={15}/>} {i}</button>)}</div><button className="primary-btn" onClick={onClose}>Готово · {pantry.length} продуктов</button></div></div>
}

function RecipeDetail({recipe,onBack,saved,onSave}) {
  const [step,setStep]=useState(1);
  const [timer,setTimer]=useState(false);
  const steps=['Подготовьте ингредиенты: нарежьте томаты и измельчите чеснок. Поставьте воду для пасты.','Отварите пасту до состояния al dente. Сохраните половину стакана воды от пасты.','Обжарьте чеснок и томаты на оливковом масле. Добавьте немного воды от пасты.','Смешайте пасту с соусом. Выложите буррату сверху и украсьте базиликом.'];
  return <div className="detail-page"><header className="topbar"><button className="back-btn" onClick={onBack}><ArrowLeft size={19}/> Назад</button><div className="brand"><div className="brand-mark"><UtensilsCrossed size={19}/></div><span>dish<span>covery</span></span></div><button className={`save-detail ${saved?'saved':''}`} onClick={onSave}>{saved?<Heart fill="currentColor"/>:<Bookmark/>}</button></header><main className="detail-main"><div className="detail-hero"><img src={recipe.image} alt={recipe.title}/><div className="detail-overlay"><span>{recipe.cuisine}</span><h1>{recipe.title}</h1><p>{recipe.description}</p><div className="detail-stats"><span><Clock3/> {recipe.time} мин</span><span><Flame/> {recipe.kcal} ккал</span><span><UtensilsCrossed/> {recipe.difficulty}</span></div></div></div><div className="detail-content"><div className="ingredients-panel"><div className="panel-title"><h2>Ингредиенты</h2><span>2 порции</span></div>{recipe.ingredients.map((i,n)=><div className="ingredient-row" key={i}><span>{i}</span><b>{['200 г','250 г','1 шт.','2 зубчика','по вкусу'][n%5]}</b></div>)}<button className="shopping-btn"><ShoppingBasket size={17}/> Добавить в список покупок</button></div><div className="steps-panel"><div className="panel-title"><div><span className="eyebrow">Приготовление</span><h2>Шаг {step} из {steps.length}</h2></div><button className="video-btn"><Play size={15} fill="currentColor"/> Видео</button></div><div className="progress"><span style={{width:`${step/steps.length*100}%`}}></span></div><div className="step-copy"><div className="step-number">{String(step).padStart(2,'0')}</div><p>{steps[step-1]}</p></div><div className="timer-box"><div><Timer/><div><strong>Таймер</strong><span>{step===2?'08:00':'03:00'}</span></div></div><button className={timer?'running':''} onClick={()=>setTimer(!timer)}>{timer?'Пауза':'Запустить'}</button></div><div className="step-nav"><button disabled={step===1} onClick={()=>setStep(s=>s-1)}><ArrowLeft/> Предыдущий</button><button disabled={step===steps.length} onClick={()=>setStep(s=>s+1)}>Следующий <ArrowRight/></button></div></div></div></main></div>
}

createRoot(document.getElementById('root')).render(<App/>);
