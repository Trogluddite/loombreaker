const express = require('express');
const app = express();
const port = 3000;

// Sample data for Markov code
const markovData = [
  { id: 1, text: 'Test 1' },
  { id: 2, text: 'Test 2' },
  { id: 3, text: 'Test 3' }
];

// Endpoint to get Markov data
app.get('/api/markov', (req, res) => {
  res.json(markovData);
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
