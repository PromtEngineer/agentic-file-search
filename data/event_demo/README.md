# Event Demo Data

Demo data for the DELL Romandie Day 2026 presentation showcasing agentic document search.

## Scenario

**Company:** TechCorp
**Event:** Team Building Event
**Attendees:** 25 employees
**Query:** "Can we accommodate everyone's dietary needs at the venue?"

## Documents

| File | Description | Agent Category | Key Content |
|------|-------------|----------------|-------------|
| guest_list.pdf | Confirmed guest list with dietary info | RELEVANT | 25 guests: 3 vegetarian, 2 vegan, 1 gluten-free (celiac), 1 severe nut allergy |
| catering_menu.pdf | Menu options and pricing | RELEVANT | Pricing: vegetarian/gluten-free included, vegan +$5/person, nut-free +$15/person. **Cross-references finance_approval.pdf** |
| venue_info.pdf | Venue details and capabilities | MAYBE | Alpine Vista Lodge, catering facilities info |
| event_details.pdf | General event information | SKIP | Date, schedule, activities |
| finance_approval.pdf | Budget approval | SKIP → BACKTRACK | **Critical:** $1,125 approved for base catering, $0 for add-ons |

## The "Eureka" Moment

The key demonstration of agentic search:

1. **Initial categorization**: Agent marks `finance_approval.pdf` as SKIP - it appears to be about financial policies, not dietary needs
2. **Cross-reference discovery**: While reading `catering_menu.pdf`, the agent finds a reference to `finance_approval.pdf` for nut-free pricing impact
3. **Backtrack**: Agent goes back to read the "skipped" document
4. **Critical finding**: Budget is $1,125 with $0 available for add-ons, but nut-free preparation costs $375 ($15 × 25 guests)

## Dietary Requirements Summary

| Guest | Requirement | Cost Impact |
|-------|-------------|-------------|
| Lisa Anderson | Vegetarian | Included |
| Rachel Green | Vegetarian | Included |
| Megan Young | Vegetarian | Included |
| David Kim | Vegan | +$5 |
| Emma Wilson | Vegan | +$5 |
| Sarah Chen | Gluten-free (celiac) | Included |
| Tom Rodriguez | SEVERE Nut Allergy | +$375 (entire event) |

**Total add-on cost:** $385 (but $0 budget available)

## Expected Agent Answer

The agent should conclude:
- ✅ **CAN accommodate**: Vegetarian (3), Gluten-free (1) - included in base price
- ⚠️ **BUDGET ISSUE**: Vegan (+$10) and Nut-free (+$375) require additional budget approval
- 📋 **Recommendation**: Request finance approval for $385 additional budget

## Regenerating Documents

The PDFs were generated from markdown files using `scripts/generate_event_docs.py`. To regenerate:

```bash
python scripts/generate_event_docs.py
```

Note: The markdown source files have been removed after PDF generation to keep the demo folder clean.
