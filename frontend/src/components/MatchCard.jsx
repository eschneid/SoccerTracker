// Convert UTC ISO string to a human-readable EST string
function toEST(isoString) {
  if (!isoString) return 'TBD';
  try {
    return new Date(isoString).toLocaleString('en-US', {
      timeZone: 'America/New_York',
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
      timeZoneName: 'short',
    });
  } catch {
    return isoString;
  }
}

const STATUS_COLORS = {
  Live:       '#22c55e',
  Scheduled:  '#3b82f6',
  Completed:  '#6b7280',
  Postponed:  '#f59e0b',
  Cancelled:  '#ef4444',
};

const RESULT_COLORS = {
  Win:  '#22c55e',
  Loss: '#ef4444',
  Draw: '#f59e0b',
};

const TEAM_ABBR = {
  'Manchester United':  'MAN UTD',
  'Manchester City':    'MAN CITY',
  'Borussia Dortmund':  'BVB',
  'Brentford FC':       'BFC',
};

export default function MatchCard({ match }) {
  const statusColor = STATUS_COLORS[match.status] || '#6b7280';
  const resultColor = RESULT_COLORS[match.result];
  const teamAbbr = TEAM_ABBR[match.team] || match.team;
  const isCompleted = match.status === 'Completed';
  const hasScore = isCompleted && match.score;

  return (
    <div className="match-card">
      <div className="card-top">
        <span className="team-abbr">{teamAbbr}</span>
        <span className="status-badge" style={{ backgroundColor: statusColor }}>
          {match.status}
        </span>
      </div>

      <div className="card-matchup">
        <span className="team-name">{match.team}</span>
        <span className="vs">vs</span>
        <span className="opponent-name">{match.opponent}</span>
      </div>

      {hasScore && (
        <div
          className="card-score"
          style={{ borderColor: resultColor || 'transparent' }}
        >
          <span className="score-text">{match.score}</span>
          {match.result && (
            <span
              className="result-pill"
              style={{ backgroundColor: resultColor }}
            >
              {match.result}
            </span>
          )}
        </div>
      )}

      <div className="card-details">
        <div className="detail-row">
          <span className="detail-icon">🕐</span>
          <span className="detail-val">{toEST(match.matchDate)}</span>
        </div>
        <div className="detail-row">
          <span className="detail-icon">🏆</span>
          <span className="detail-val">{match.competition}</span>
          {match.league && match.league !== match.competition && (
            <span className="detail-sub">&nbsp;· {match.league}</span>
          )}
        </div>
        <div className="detail-row">
          <span className="detail-icon">{match.homeAway === 'Home' ? '🏠' : '✈️'}</span>
          <span className="detail-val">{match.homeAway}</span>
        </div>
        {match.venue && match.venue !== 'TBD' && (
          <div className="detail-row">
            <span className="detail-icon">📍</span>
            <span className="detail-val">{match.venue}</span>
          </div>
        )}
      </div>
    </div>
  );
}
