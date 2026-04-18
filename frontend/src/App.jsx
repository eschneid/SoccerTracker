import { useState, useEffect } from 'react';
import MatchCard from './components/MatchCard.jsx';
import './App.css';

const TEAMS = ['Manchester United', 'Manchester City', 'Borussia Dortmund', 'Brentford FC'];

async function fetchMatches(endpoint) {
  const res = await fetch(`/api/matches/${endpoint}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  const data = await res.json();
  return data.matches;
}

function countByTeam(matches, team) {
  return matches.filter((m) => m.team === team).length;
}

export default function App() {
  const [upcoming, setUpcoming] = useState([]);
  const [recent, setRecent] = useState([]);
  const [activeTab, setActiveTab] = useState('upcoming');
  const [activeTeam, setActiveTeam] = useState('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [up, re] = await Promise.all([
          fetchMatches('upcoming'),
          fetchMatches('recent'),
        ]);
        setUpcoming(up);
        setRecent(re);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const sourceMatches = activeTab === 'upcoming' ? upcoming : recent;
  const filteredMatches =
    activeTeam === 'All'
      ? sourceMatches
      : sourceMatches.filter((m) => m.team === activeTeam);

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <span className="header-icon">⚽</span>
          <h1>SoccerTracker</h1>
          <p className="header-sub">Match dashboard</p>
        </div>
      </header>

      <main className="app-main">
        <div className="tab-bar">
          <button
            className={`tab-btn ${activeTab === 'upcoming' ? 'active' : ''}`}
            onClick={() => setActiveTab('upcoming')}
          >
            Upcoming
            <span className="badge">{upcoming.length}</span>
          </button>
          <button
            className={`tab-btn ${activeTab === 'recent' ? 'active' : ''}`}
            onClick={() => setActiveTab('recent')}
          >
            Recent Results
            <span className="badge">{recent.length}</span>
          </button>
        </div>

        <div className="team-filter">
          <button
            className={`team-btn ${activeTeam === 'All' ? 'active' : ''}`}
            onClick={() => setActiveTeam('All')}
          >
            All Teams
          </button>
          {TEAMS.map((team) => {
            const count =
              activeTab === 'upcoming'
                ? countByTeam(upcoming, team)
                : countByTeam(recent, team);
            return (
              <button
                key={team}
                className={`team-btn ${activeTeam === team ? 'active' : ''}`}
                onClick={() => setActiveTeam(team)}
              >
                {team}
                {count > 0 && <span className="badge">{count}</span>}
              </button>
            );
          })}
        </div>

        {loading && (
          <div className="state-msg">
            <div className="spinner" />
            <p>Loading matches...</p>
          </div>
        )}

        {error && (
          <div className="state-msg error">
            <p>Failed to load matches: {error}</p>
            <p className="hint">Make sure the backend is running on port 3001.</p>
          </div>
        )}

        {!loading && !error && filteredMatches.length === 0 && (
          <div className="state-msg">
            <p>
              No {activeTab} matches
              {activeTeam !== 'All' ? ` for ${activeTeam}` : ''}.
            </p>
          </div>
        )}

        {!loading && !error && filteredMatches.length > 0 && (
          <div className="match-grid">
            {filteredMatches.map((match) => (
              <MatchCard key={match.id} match={match} />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
