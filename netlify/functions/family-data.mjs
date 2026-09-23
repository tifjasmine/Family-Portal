const BASE = "app9p5zQt007Krvig";
const TASKS = "tbl4CF1nd61UrsF8t";
const CALENDAR = "tblrFGYKimflK7G7Z";
const COMPLETIONS = "tblIwRJXtyWoiFJBl";

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
const choices = value => Array.isArray(value) ? value.map(choice) : value ? [choice(value)] : [];
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
    stars: Math.max(1, Number(fields["Bonus Stars"] || 1)),
  };
}

async function airtable(url, token, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { Authorization: `Bearer ${token}`, "content-type":"application/json", ...(options.headers || {}) },
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(`Airtable ${response.status}: ${body.error?.message || body.error?.type || "request failed"}`);
  return body;
}

async function saveCompletion(token, key, completed) {
  const match = /^d:(\d{4}-\d{2}-\d{2}):(rec[A-Za-z0-9]+):(Morning|Afternoon|Evening|Anytime)$/.exec(key);
  if (!match || !Number.isFinite(Date.parse(`${match[1]}T12:00:00Z`))) throw new Error("Invalid task completion");
  const [, date, taskId, slot] = match;
  const task = await airtable(`https://api.airtable.com/v0/${BASE}/${TASKS}/${taskId}`, token);
  const who = choice(task.fields?.Who);
  if (!["Kaiya","Mom","Dad"].includes(who)) throw new Error("Task has no valid person");
  const fields = {
    Completion:key,
    Task:task.fields?.Task || taskId,
    Who:who,
    Date:date,
    Completed:completed,
  };
  if (slot !== "Anytime") fields["Time of Day"] = slot;
  const result = await airtable(`https://api.airtable.com/v0/${BASE}/${encodeURIComponent(COMPLETIONS)}`, token, {
    method:"PATCH",
    body:JSON.stringify({ performUpsert:{ fieldsToMergeOn:["Completion"] }, records:[{ fields }] }),
  });
  return result.records?.[0]?.id;
}

export async function handler(event) {
  const token = process.env.AIRTABLE_TOKEN;
  if (!token) return json(503, { error:"Airtable sync is not configured" });
  if (event?.httpMethod === "POST") {
    if (event.headers?.["x-portal-pin"] !== "123") return json(401, { error:"Unlock the portal first" });
    let body;
    try { body = JSON.parse(event.body || "{}"); } catch { return json(400, { error:"Invalid request" }); }
    if (typeof body.key !== "string" || typeof body.completed !== "boolean") return json(400, { error:"Invalid completion" });
    try {
      const id = await saveCompletion(token, body.key, body.completed);
      return json(200, { saved:true, id, key:body.key, completed:body.completed });
    } catch (error) {
      return json(502, { error:error.message || "Could not save completion" });
    }
  }
  if (event?.httpMethod && event.httpMethod !== "GET") return json(405, { error:"Method not allowed" });
  try {
    const [taskRecords, calendarRecords, completionRecords] = await Promise.all([records(TASKS, token), records(CALENDAR, token), records(COMPLETIONS, token)]);
    const calendarNames = new Set(calendarRecords.map(r => r.fields && r.fields.Event).filter(Boolean));
    const tasks = taskRecords
      .filter(r => r.fields && r.fields.Active !== false && r.fields.Task !== "Kaiya daily check-in" && !calendarNames.has(r.fields.Task))
      .map(r => item(r, "task"));
    const calendar = calendarRecords
      .filter(r => r.fields && r.fields.Active === true)
      .map(r => item(r, "plan"));
    const items = tasks.concat(calendar).filter(x => x.who.length && (x.repeat.kind !== "date" || x.repeat.date));
    items.sort((a,b) => a.sort-b.sort || a.title.localeCompare(b.title));
    const completions = completionRecords.filter(r => typeof r.fields?.Completion === "string")
      .map(r => ({ key:r.fields.Completion, completed:r.fields.Completed === true }));
    return json(200, { items, completions, syncedAt:new Date().toISOString() });
  } catch (error) {
    return json(502, { error:error.message || "Could not load Airtable" });
  }
}
