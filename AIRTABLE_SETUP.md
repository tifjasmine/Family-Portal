# Airtable structure for Family Portal

Use one Airtable base named **Family Portal**. Keep people in linked records instead of making one table per person; that makes recurring items reusable while still allowing a separate filtered view for Kaiya, Mom, and Dad.

## 1. People

| Field | Type | Example |
| --- | --- | --- |
| Name | Single line text (primary) | Kaiya |
| Portal ID | Single line text | daughter |
| Avatar | Attachment (optional) | portrait |
| Color | Single select (optional) | Purple |
| Active | Checkbox | checked |

Create records for **Kaiya**, **Mom**, and **Dad**.

## 2. Routine Tasks

Use this for things that can be checked off, such as brushing teeth or packing snacks.

| Field | Type | Example |
| --- | --- | --- |
| Task | Single line text (primary) | Brush teeth |
| Emoji | Single line text | 🪥 |
| People | Link to People, allow multiple | Kaiya |
| Time of Day | Multiple select | Morning, Evening |
| Recurrence | Single select | Weekly |
| Days | Multiple select | Mon, Tue, Thu |
| Start Date | Date (optional) | 2026-09-21 |
| End Date | Date (optional) | blank |
| Sort Order | Number | 10 |
| Active | Checkbox | checked |

Recommended `Recurrence` choices: **Daily**, **Weekly**, and **One date**.

## 3. Schedule

Use this for items that describe **My day** but are not checked off.

| Field | Type | Example |
| --- | --- | --- |
| Activity | Single line text (primary) | School |
| Emoji | Single line text | 🏫 |
| People | Link to People, allow multiple | Kaiya |
| Time of Day | Single select | Morning |
| Recurrence | Single select | Weekly |
| Days | Multiple select | Mon, Tue, Thu |
| Pickup Person | Single line text (optional) | Gigi / PopPop |
| Start Date | Date (optional) | blank |
| End Date | Date (optional) | blank |
| Sort Order | Number | 10 |
| Active | Checkbox | checked |

Example recurring records:

| Activity | Time of Day | Days |
| --- | --- | --- |
| School | Morning | Mon, Tue, Thu |
| Gigi / PopPop pick up | Afternoon | Mon, Tue, Thu |

## 4. Completions

Use one record per completed task occurrence. This preserves history instead of overwriting the routine.

| Field | Type | Example |
| --- | --- | --- |
| Completion | Formula (primary) | task + date + time |
| Routine Task | Link to Routine Tasks | Brush teeth |
| Person | Link to People | Kaiya |
| Date | Date | 2026-09-21 |
| Time of Day | Single select | Morning |
| Completed | Checkbox | checked |
| Completed At | Created time | automatic |

## 5. Learning Activities

Use this optional table when you want to choose or override the automatically rotating letter lesson.

| Field | Type | Example |
| --- | --- | --- |
| Letter | Single line text (primary) | A |
| Example Word | Single line text | Apple |
| Emoji | Single line text | 🍎 |
| Sound Prompt | Long text | Short A says “ah” |
| Lesson Date | Date (optional) | 2026-09-21 |
| Active | Checkbox | checked |

## 6. Workouts

Store reusable movement cards here. The portal can select three active exercises each morning.

| Field | Type | Example |
| --- | --- | --- |
| Exercise | Single line text (primary) | Star jumps |
| Emoji | Single line text | ⭐ |
| Instruction | Single line text | 5 jumps |
| Difficulty | Single select | Easy |
| Active | Checkbox | checked |

## Recommended views

In **Routine Tasks**, create filtered views: `Kaiya Tasks`, `Mom Tasks`, and `Dad Tasks`.

In **Schedule**, create filtered views: `Kaiya My Day`, `Mom My Day`, and `Dad My Day`.

Filter each view by the linked `People` record and `Active` being checked. Group by `Time of Day`, then sort by `Sort Order`.

## Web integration note

Do not put an Airtable personal access token directly in `index.html`; anyone visiting the site could read it. The Netlify site should call a Netlify Function, and that server-side function should use an `AIRTABLE_TOKEN` environment variable to talk to Airtable.
