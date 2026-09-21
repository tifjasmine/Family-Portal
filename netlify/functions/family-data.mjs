const BASE = "app9p5zQt007Krvig";
const TASKS = "tbl4CF1nd61UrsF8t";
const CALENDAR = "tblrFGYKimflK7G7Z";

const json = (statusCode, body) => ({
  statusCode,
  headers: { "content-type": "application/json", "cache-control": "no-store" },
  body: JSON.stringify(body),
});

async function records(table, token) {
  const all = [];
  let offset = "";
  do {
    const url = new URL(`https://api.airtable.com/v0/${BASE}/${table}`);
    url.searchParams.set("pageSize", "100");
    if (offset) url.searchParams.set("offset", offset);
    const response = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
    if (!response.ok) throw new Error(`Airtable returned ${response.status}`);
    const page = await response.json();
    all.push(...page.records);
    offset = page.offset || "";
  } while (offset);
  return all;
}

const choice = value => value && typeof value === "object" ? value.name : value;
const choices = value => (Array.isArray(value) ? value.map(choice) : []);
const dayNumber = { Sun:0, Mon:1, Tue:2, Wed:3, Thu:4, Fri:5, Sat:6 };
const person = { Kaiya:"daughter", Mom:"mom", Dad:"dad" };

function repeat(fields) {
  const kind = choice(fields.Repeat);
  if (kind === "Every day") return { kind:"daily" };
  if (kind === "Selected weekdays") return { kind:"days", days:choices(fields.Days).map(x => dayNumber[x]).filter(x => x !== undefined) };
  return { kind:"date", date:fields.Date || "" };
}

function item(record, type) {
  const fields = record.fields || {};
  const who = person[choice(fields.Who)];
  return {
    id: record.id,
    title: fields.Task || fields.Event || "Untitled",
    emoji: fields.Emoji || (type === "plan" ? "📅" : "⭐"),
    who: who ? [who] : [],
    type,
    repeat: repeat(fields),
    slots: choices(fields["Time of Day"]),
    sort: Number(fields["Sort Order"] || 999),
  };
}

export async function handler() {
  const token = process.env.AIRTABLE_TOKEN;
  if (!token) return json(503, { error:"Airtable sync is not configured" });
  try {
    const [taskRecords, calendarRecords] = await Promise.all([records(TASKS, token), records(CALENDAR, token)]);
    const calendarNames = new Set(calendarRecords.map(r => r.fields && r.fields.Event).filter(Boolean));
    const tasks = taskRecords
      .filter(r => r.fields && r.fields.Active !== false && r.fields.Task !== "Kaiya daily check-in" && !calendarNames.has(r.fields.Task))
      .map(r => item(r, "task"));
    const calendar = calendarRecords
      .filter(r => r.fields && r.fields.Active === true)
      .map(r => item(r, "plan"));
    const items = tasks.concat(calendar).filter(x => x.who.length && (x.repeat.kind !== "date" || x.repeat.date));
    items.sort((a,b) => a.sort-b.sort || a.title.localeCompare(b.title));
    return json(200, { items, syncedAt:new Date().toISOString() });
  } catch (error) {
    return json(502, { error:error.message || "Could not load Airtable" });
  }
}

