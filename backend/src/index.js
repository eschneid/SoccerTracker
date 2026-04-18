const express = require('express');
const cors = require('cors');
const { Client } = require('@notionhq/client');
require('dotenv').config({ path: '../.env' });

const app = express();
const PORT = 3001;

// Allow Vite dev server
app.use(cors({
  origin: ['http://localhost:5173', 'http://127.0.0.1:5173'],
  methods: ['GET'],
}));

app.use(express.json());

const notion = new Client({ auth: process.env.NOTION_TOKEN });
const DATABASE_ID = process.env.NOTION_DATABASE_ID;

// Extract a plain match object from a Notion page
function extractMatch(page) {
  const p = page.properties;
  const getRichText = (prop) => prop?.rich_text?.[0]?.text?.content ?? '';
  const getSelect   = (prop) => prop?.select?.name ?? '';
  const getTitle    = (prop) => prop?.title?.[0]?.text?.content ?? '';
  const getNumber   = (prop) => prop?.number ?? null;
  const getDate     = (prop) => prop?.date?.start ?? null;

  return {
    id:           page.id,
    opponent:     getTitle(p['Opponent']),
    team:         getSelect(p['Team']),
    matchDate:    getDate(p['Match Date']),
    league:       getSelect(p['League']),
    competition:  getSelect(p['Competition']),
    homeAway:     getSelect(p['Home/Away']),
    result:       getSelect(p['Result']),
    status:       getSelect(p['Status']),
    venue:        getRichText(p['Venue']),
    season:       getSelect(p['Season']),
    matchId:      getRichText(p['Match ID']),
    score:        getRichText(p['Score']),
    goalsFor:     getNumber(p['Goals For']),
    goalsAgainst: getNumber(p['Goals Against']),
    lastUpdated:  getDate(p['Last Updated']),
  };
}

// Paginate through all Notion results (API max is 100 per call)
async function queryAllPages(filter, sorts) {
  let results = [];
  let startCursor = undefined;
  let hasMore = true;

  while (hasMore) {
    const response = await notion.databases.query({
      database_id: DATABASE_ID,
      filter,
      sorts,
      start_cursor: startCursor,
      page_size: 100,
    });
    results = results.concat(response.results);
    hasMore = response.has_more;
    startCursor = response.next_cursor;
  }

  return results;
}

// GET /api/matches/upcoming — Scheduled or Live, ascending by date
app.get('/api/matches/upcoming', async (req, res) => {
  try {
    const filter = {
      or: [
        { property: 'Status', select: { equals: 'Scheduled' } },
        { property: 'Status', select: { equals: 'Live' } },
      ],
    };
    const sorts = [{ property: 'Match Date', direction: 'ascending' }];
    const pages = await queryAllPages(filter, sorts);
    const matches = pages.map(extractMatch);
    res.json({ matches, count: matches.length });
  } catch (err) {
    console.error('Error fetching upcoming matches:', err.message);
    res.status(500).json({ error: 'Failed to fetch upcoming matches', detail: err.message });
  }
});

// GET /api/matches/recent — last 20 Completed matches, descending by date
app.get('/api/matches/recent', async (req, res) => {
  try {
    const filter = { property: 'Status', select: { equals: 'Completed' } };
    const sorts = [{ property: 'Match Date', direction: 'descending' }];
    const pages = await queryAllPages(filter, sorts);
    const matches = pages.slice(0, 20).map(extractMatch);
    res.json({ matches, count: matches.length });
  } catch (err) {
    console.error('Error fetching recent matches:', err.message);
    res.status(500).json({ error: 'Failed to fetch recent matches', detail: err.message });
  }
});

// GET /api/health — sanity check
app.get('/api/health', (req, res) => {
  res.json({
    status: 'ok',
    databaseId: DATABASE_ID ? 'configured' : 'MISSING',
  });
});

app.listen(PORT, () => {
  console.log(`SoccerTracker API running on http://localhost:${PORT}`);
  console.log(`NOTION_DATABASE_ID: ${DATABASE_ID ? DATABASE_ID.slice(0, 8) + '...' : 'NOT SET'}`);
});
