# Clean Airtable setup for Family Portal

Use one base named **Family Portal** with three practical tables. `Tasks` holds things that can be checked off, `Calendar` holds “My Day” activities, and `Completions` preserves daily progress.

This setup deliberately uses a simple **Who** single-select instead of linked People records. Adding an item should feel like completing a short form.

## 1. Tasks

| Field | Airtable type | Choices / purpose |
| --- | --- | --- |
| Task | Single line text (primary) | Brush teeth |
| Who | Single select | Kaiya, Mom, Dad |
| Emoji | Single line text | 🪥 |
| Repeat | Single select | Every day, Selected weekdays, One-time |
| Days | Multiple select | Sun, Mon, Tue, Wed, Thu, Fri, Sat |
| Date | Date | Used only for One-time |
| Time of Day | Multiple select | Morning, Afternoon, Evening |
| Sort Order | Number | Optional ordering, such as 10, 20, 30 |
| Active | Checkbox | Show the task in the portal |

Examples:

| Task | Who | Repeat | Days | Date | Time of Day |
| --- | --- | --- | --- | --- | --- |
| Brush teeth | Kaiya | Every day | | | Morning, Evening |
| Pack snacks | Mom | One-time | | Sep 24, 2026 | Evening |

## 2. Calendar

Calendar records appear in **My Day** and are not checkboxes.

| Field | Airtable type | Choices / purpose |
| --- | --- | --- |
| Event | Single line text (primary) | School |
| Who | Single select | Kaiya, Mom, Dad |
| Emoji | Single line text | 🏫 |
| Repeat | Single select | Every day, Selected weekdays, One-time |
| Days | Multiple select | Sun, Mon, Tue, Wed, Thu, Fri, Sat |
| Date | Date | Used only for One-time |
| Time of Day | Single select | Morning, Afternoon, Evening |
| Details | Long text | Optional note or pickup person |
| Sort Order | Number | Optional ordering |
| Active | Checkbox | Show the event in the portal |

Examples:

| Event | Who | Repeat | Days | Date | Time of Day |
| --- | --- | --- | --- | --- | --- |
| School | Kaiya | Selected weekdays | Mon, Tue, Thu | | Morning |
| Gigi / PopPop pick up | Kaiya | Selected weekdays | Mon, Tue, Thu | | Afternoon |
| Dentist | Kaiya | One-time | | Oct 8, 2026 | Afternoon |

## 3. Completions

The app creates these records; they are not part of everyday Airtable data entry.

| Field | Airtable type | Purpose |
| --- | --- | --- |
| Completion | Single line text (primary) | A readable unique label |
| Task | Link to Tasks | The completed routine |
| Who | Single select | Kaiya, Mom, Dad |
| Date | Date | Day completed |
| Time of Day | Single select | Morning, Afternoon, Evening |
| Completed | Checkbox | Completion state |
| Completed At | Created time | Automatic timestamp |

## Views that keep Airtable tidy

Create these views in both `Tasks` and `Calendar`:

- `Kaiya` — filter `Who is Kaiya` and `Active is checked`
- `Mom` — filter `Who is Mom` and `Active is checked`
- `Dad` — filter `Who is Dad` and `Active is checked`
- `Inactive` — filter `Active is not checked`

Group active views by `Time of Day`, then sort by `Sort Order`.

## Matching app form

The grown-up editor uses the same choices as Airtable:

1. Name and emoji
2. Who: Kaiya, Mom, or Dad
3. Goes on: Tasks or Calendar / My Day
4. One-time or recurring
5. Date or selected weekdays
6. Time of day

App edits currently stay in the browser until the Airtable connection is configured. Never place an Airtable token in `index.html`; the Netlify Function should hold it securely in an `AIRTABLE_TOKEN` environment variable.
