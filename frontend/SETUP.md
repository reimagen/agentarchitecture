# Workflow Analyzer Frontend

A React-based frontend application for analyzing workflow automation potential.

## Features

- **File Upload**: Upload workflow files (JSON, TXT, YAML)
- **Step Analysis**: View detailed cards for each workflow step with:
  - ID and description
  - Automation feasibility score
  - Human review requirements
  - Risk level assessment
  - Agent type classification
  - Suggested tools
  - Determinism score

- **Summary Dashboard**: Overview statistics including:
  - Total steps count
  - Automatable steps count
  - Agent-required steps
  - Human-required steps
  - High-risk and critical-risk step counts
  - Overall automation potential percentage

- **Key Insights**: Expandable insight cards showing:
  - Automation potential summary
  - Manual review bottlenecks
  - Affected steps identification
  - Priority levels (HIGH, MEDIUM, LOW)

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── FileUpload.js       # File upload component
│   │   ├── FileUpload.css
│   │   ├── StepsList.js        # Container for step cards
│   │   ├── StepsList.css
│   │   ├── StepCard.js         # Individual step card
│   │   ├── StepCard.css
│   │   ├── SummaryContainer.js # Summary statistics
│   │   ├── SummaryContainer.css
│   │   ├── KeyInsights.js      # Key insights display
│   │   └── KeyInsights.css
│   ├── App.js                  # Main app component
│   ├── App.css                 # App styling
│   └── index.js
└── package.json
```

## Setup Instructions

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies** (if not already done):
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The app will open at `http://localhost:3000`

4. **Configure Backend URL**:
   - Edit `src/App.js` line 22
   - Update the fetch URL to match your backend API endpoint
   - Default: `http://localhost:8000/api/analyze-workflow`

## Backend Integration

The frontend expects a POST endpoint that:
- Accepts a `multipart/form-data` file upload
- Returns JSON with the following structure:

```json
{
  "steps": [
    {
      "id": "step_1",
      "description": "Step description",
      "automation_feasibility": 0.85,
      "requires_human_review": false,
      "risk_level": "low",
      "agent_type": "autonomous",
      "suggested_tools": ["tool1", "tool2"],
      "determinism_score": 0.9
    }
  ],
  "summary": {
    "high_risk_steps": 2,
    "total_steps": 10,
    "automatable_count": 7,
    "agent_required_count": 8,
    "human_required_count": 2,
    "automation_potential": 0.7,
    "critical_risk_steps": 0
  },
  "key_insights": [
    {
      "title": "Strong Automation Potential",
      "description": "7/10 steps (70%) can be automated",
      "priority": "HIGH",
      "affected_steps": ["step_1", "step_2", "step_3", "step_4", "step_5", "step_6", "step_10"]
    }
  ]
}
```

## Available Scripts

- `npm start`: Run development server
- `npm build`: Build for production
- `npm test`: Run tests
- `npm eject`: Eject from Create React App (irreversible)

## Responsive Design

The application is responsive and works on:
- Desktop (1400px max-width centered layout)
- Tablet (single column on screens < 1024px)
- Mobile (full-width responsive layout)

## Styling

- Uses CSS Grid and Flexbox for layout
- Smooth transitions and animations
- Color-coded priority indicators
- Interactive components with hover effects

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
