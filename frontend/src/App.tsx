import { useState, useEffect } from 'react'
import api from './api/client'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'

const AUTHOR_ID = '7b4347d0-1e1b-40b0-bc26-8c9728a7e92f'

interface Book { id: string; title: string; review_count: number; total_llm_cost_usd: number }
interface Review { id: string; review_text: string; sentiment: string; themes: string[]; summary: string; rating: number; is_actionable: boolean }
interface Highlights { loved: string; complaint: string; fix: string }

const COLORS: Record<string, string> = { positive: '#22c55e', mixed: '#f59e0b', negative: '#ef4444' }

function Stars({ rating }: { rating: number }) {
  return <div className="stars">{[1,2,3,4,5].map(i => <span key={i} className={i <= rating ? 'star-filled' : 'star-empty'}>★</span>)}</div>
}

function HighlightsCard({ bookId }: { bookId: string }) {
  const [highlights, setHighlights] = useState<Highlights|null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get(`/books/${bookId}/highlights`, { params: { author_id: AUTHOR_ID } })
      .then(r => setHighlights(r.data))
      .finally(() => setLoading(false))
  }, [bookId])

  return (
    <div className="card fade-up-2" style={{marginBottom:'1.25rem', background:'linear-gradient(135deg, rgba(124,58,237,0.08), rgba(167,139,250,0.08))'}}>
      <div className="section-title">✨ AI Highlights</div>
      {loading ? (
        <div style={{display:'flex', alignItems:'center', gap:'0.5rem', color:'#9ca3af', fontSize:'0.875rem'}}>
          <div className="spinner" style={{width:'16px',height:'16px',margin:0}}></div>
          Analyzing reviews...
        </div>
      ) : highlights ? (
        <div style={{display:'flex', flexDirection:'column', gap:'0.75rem'}}>
          <div style={{display:'flex', gap:'0.75rem', alignItems:'flex-start'}}>
            <span style={{fontSize:'1.25rem'}}>💚</span>
            <div>
              <div style={{fontSize:'0.7rem', fontWeight:600, color:'#22c55e', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:'0.2rem'}}>What readers loved</div>
              <div style={{fontSize:'0.875rem', color:'#374151'}}>{highlights.loved}</div>
            </div>
          </div>
          <div style={{display:'flex', gap:'0.75rem', alignItems:'flex-start'}}>
            <span style={{fontSize:'1.25rem'}}>🔴</span>
            <div>
              <div style={{fontSize:'0.7rem', fontWeight:600, color:'#ef4444', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:'0.2rem'}}>Main complaint</div>
              <div style={{fontSize:'0.875rem', color:'#374151'}}>{highlights.complaint}</div>
            </div>
          </div>
          <div style={{display:'flex', gap:'0.75rem', alignItems:'flex-start'}}>
            <span style={{fontSize:'1.25rem'}}>📝</span>
            <div>
              <div style={{fontSize:'0.7rem', fontWeight:600, color:'#7c3aed', textTransform:'uppercase', letterSpacing:'0.05em', marginBottom:'0.2rem'}}>Fix for next book</div>
              <div style={{fontSize:'0.875rem', color:'#374151'}}>{highlights.fix}</div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  )
}

function CatalogView({ books, onSelect }: { books: Book[], onSelect: (b: Book) => void }) {
  return (
    <div className="fade-up">
      <div className="page-title">Your Catalog</div>
      <div className="page-subtitle">{books.length} books · click to explore reviews</div>
      <div className="grid-3">
        {books.map((book, i) => (
          <div key={book.id} className={`card card-clickable fade-up-${Math.min(i+2,4)}`} onClick={() => onSelect(book)}>
            <div className="book-icon">📖</div>
            <div className="book-title">{book.title}</div>
            <div style={{fontSize:'0.85rem', color:'#6b7280'}}>{book.review_count} reviews</div>
            <div className="book-meta">
              <span>LLM cost: ${book.total_llm_cost_usd.toFixed(4)}</span>
              <span className="view-link">View →</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

function BookDetail({ book }: { book: Book }) {
  const [reviews, setReviews] = useState<Review[]>([])
  const [sentiment, setSentiment] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    const params: Record<string,string> = { author_id: AUTHOR_ID }
    if (sentiment) params.sentiment = sentiment
    api.get(`/reviews/book/${book.id}`, { params })
      .then(r => setReviews(r.data))
      .finally(() => setLoading(false))
  }, [book.id, sentiment])

  const sentimentCounts = reviews.reduce((acc, r) => { acc[r.sentiment] = (acc[r.sentiment]||0)+1; return acc }, {} as Record<string,number>)
  const pieData = Object.entries(sentimentCounts).map(([name,value]) => ({name,value}))
  const themeCounts = reviews.flatMap(r => r.themes||[]).reduce((acc,t) => { acc[t]=(acc[t]||0)+1; return acc }, {} as Record<string,number>)
  const themeData = Object.entries(themeCounts).sort((a,b)=>b[1]-a[1]).slice(0,6).map(([name,value])=>({name,value}))

  return (
    <div className="fade-up">
      <div style={{display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:'1.5rem'}}>
        <div>
          <div className="page-title">{book.title}</div>
          <div className="page-subtitle">{book.review_count} reviews · ${book.total_llm_cost_usd.toFixed(4)} LLM spend</div>
        </div>
        <select className="select" value={sentiment} onChange={e => setSentiment(e.target.value)}>
          <option value="">All sentiments</option>
          <option value="positive">Positive</option>
          <option value="mixed">Mixed</option>
          <option value="negative">Negative</option>
        </select>
      </div>

      <HighlightsCard bookId={book.id} />

      <div className="grid-2 fade-up-2" style={{marginBottom:'1.25rem'}}>
        <div className="card">
          <div className="section-title">Sentiment Distribution</div>
          <ResponsiveContainer width="100%" height={180}>
            <PieChart>
              <Pie data={pieData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({name,value})=>`${name}: ${value}`}>
                {pieData.map(e => <Cell key={e.name} fill={COLORS[e.name]||'#6366f1'} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="card">
          <div className="section-title">Top Themes</div>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart data={themeData} layout="vertical">
              <XAxis type="number" hide />
              <YAxis type="category" dataKey="name" width={90} tick={{fontSize:11}} />
              <Tooltip />
              <Bar dataKey="value" fill="#7c3aed" radius={[0,4,4,0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card fade-up-3">
        <div className="section-title">Reviews</div>
        {loading ? (
          <div className="loading"><div className="spinner"></div>Loading reviews...</div>
        ) : reviews.map(r => (
          <div key={r.id} className="review-card">
            <div className="review-header">
              <div style={{display:'flex', alignItems:'center', gap:'0.5rem'}}>
                <span className={`badge badge-${r.sentiment}`}>{r.sentiment}</span>
                <Stars rating={r.rating} />
              </div>
              {r.is_actionable && <span className="actionable">⚡ Actionable</span>}
            </div>
            <div className="review-summary">{r.summary}</div>
            <div className="review-text">{r.review_text}</div>
            <div className="tags">{(r.themes||[]).map(t => <span key={t} className="tag">{t}</span>)}</div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function App() {
  const [books, setBooks] = useState<Book[]>([])
  const [selectedBook, setSelectedBook] = useState<Book|null>(null)
  const [view, setView] = useState<'catalog'|'book'>('catalog')
  const [loading, setLoading] = useState(true)
  const [newTitle, setNewTitle] = useState('')
  const [adding, setAdding] = useState(false)

  useEffect(() => {
    api.get(`/books/author/${AUTHOR_ID}`).then(r => setBooks(r.data)).finally(() => setLoading(false))
  }, [])

  const addBook = async () => {
    if (!newTitle.trim()) return
    setAdding(true)
    try {
      await api.post('/books/', { author_id: AUTHOR_ID, title: newTitle })
      setNewTitle('')
      const r = await api.get(`/books/author/${AUTHOR_ID}`)
      setBooks(r.data)
    } finally { setAdding(false) }
  }

  return (
    <>
      <span className="deco-star" style={{top:'15%', left:'5%', animation:'float 4s ease-in-out infinite'}}>✦</span>
      <span className="deco-star" style={{top:'60%', right:'4%', animation:'float 3s ease-in-out infinite 1s', fontSize:'1rem'}}>✦</span>
      <span className="deco-star" style={{top:'35%', right:'8%', animation:'float 5s ease-in-out infinite 0.5s', fontSize:'0.75rem'}}>✦</span>

      <header>
        <div className="logo">
          <span className="star">✦</span>
          ReviewPulse
        </div>
        <div style={{display:'flex', gap:'0.75rem', alignItems:'center'}}>
          <input
            className="input"
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && addBook()}
            placeholder="Add a book title..."
            style={{width:'200px'}}
          />
          <button className="btn-primary" onClick={addBook} disabled={adding}>
            {adding ? 'Adding...' : '+ Add Book'}
          </button>
        </div>
      </header>

      <nav>
        <button className={`nav-btn ${view==='catalog'?'active':''}`} onClick={() => setView('catalog')}>Catalog</button>
        {selectedBook && (
          <button className={`nav-btn ${view==='book'?'active':''}`} onClick={() => setView('book')}>{selectedBook.title}</button>
        )}
      </nav>

      <main>
        {loading ? (
          <div className="loading"><div className="spinner"></div>Loading your catalog...</div>
        ) : view === 'catalog' ? (
          <CatalogView books={books} onSelect={b => { setSelectedBook(b); setView('book') }} />
        ) : selectedBook ? (
          <BookDetail book={selectedBook} />
        ) : null}
      </main>
    </>
  )
}