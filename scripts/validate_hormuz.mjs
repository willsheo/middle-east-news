import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const dataDir = path.join(root, "data");
const startDate = "2026-01-01";
const endDate = "2026-07-24";

const dailyNumeric = new Set([
  "verified_crossings_all",
  "verified_crossings_all_alt",
  "commodity_vessel_crossings",
  "tanker_crossings",
  "crude_tanker_crossings",
  "oil_product_tanker_crossings",
  "lng_carrier_crossings",
  "lpg_carrier_crossings",
  "inbound_crossings",
  "outbound_crossings",
  "oil_volume_million_bbl",
  "korea_operated_crossings",
  "korea_bound_energy_crossings",
  "korea_bound_oil_million_bbl",
]);
const coverageStatuses = new Set([
  "no_daily_report_found",
  "aggregate_only",
  "reported_daily",
  "reported_partial",
  "conflict",
  "provisional",
]);
const qualifiers = new Set(["", "exact", "approximate", "lower_bound", "upper_bound"]);
const qualityFlags = new Set([
  "exact",
  "approximate",
  "lower_bound",
  "upper_bound",
  "partial_window",
  "conflict",
  "aggregate_only",
]);

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function parseCsv(text, name) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;

  for (let index = 0; index < text.length; index += 1) {
    const character = text[index];
    if (quoted) {
      if (character === '"' && text[index + 1] === '"') {
        field += '"';
        index += 1;
      } else if (character === '"') {
        quoted = false;
      } else {
        field += character;
      }
    } else if (character === '"') {
      quoted = true;
    } else if (character === ",") {
      row.push(field);
      field = "";
    } else if (character === "\n") {
      row.push(field.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      field = "";
    } else {
      field += character;
    }
  }
  assert(!quoted, name + ": unterminated quoted field");
  if (field || row.length) {
    row.push(field.replace(/\r$/, ""));
    rows.push(row);
  }

  const headers = rows.shift();
  assert(headers && headers.length, name + ": missing header");
  return rows.map((values, index) => {
    assert(
      values.length === headers.length,
      name + ":" + (index + 2) + ": expected " + headers.length +
        " fields, found " + values.length,
    );
    return Object.fromEntries(headers.map((header, column) => [header, values[column]]));
  });
}

function readCsv(name) {
  const text = fs.readFileSync(path.join(dataDir, name), "utf8").replace(/^\uFEFF/, "");
  return parseCsv(text, name);
}

function parseIsoDate(value, context) {
  assert(/^\d{4}-\d{2}-\d{2}$/.test(value), context + ": invalid ISO date " + value);
  const parsed = new Date(value + "T00:00:00Z");
  assert(
    !Number.isNaN(parsed.valueOf()) && parsed.toISOString().slice(0, 10) === value,
    context + ": invalid calendar date " + value,
  );
  return parsed;
}

function parseNonnegative(value, context) {
  if (value === "") return;
  const number = Number(value);
  assert(Number.isFinite(number), context + ": non-numeric value " + value);
  assert(number >= 0, context + ": negative value " + value);
}

function splitSources(value) {
  return value.split(";").filter(Boolean);
}

function dateRange(start, end) {
  const result = [];
  const endValue = parseIsoDate(end, "range end");
  for (
    let cursor = parseIsoDate(start, "range start");
    cursor <= endValue;
    cursor = new Date(cursor.valueOf() + 86_400_000)
  ) {
    result.push(cursor.toISOString().slice(0, 10));
  }
  return result;
}

const sources = readCsv("hormuz_sources.csv");
const sourceIds = new Set(sources.map((row) => row.source_id));
assert(sourceIds.size === sources.length, "duplicate source_id");
for (const row of sources) {
  assert(row.source_type === "media", row.source_id + ": source must be media");
  assert(/^https?:\/\/[^/]+/.test(row.url), row.source_id + ": invalid URL");
  parseIsoDate(row.published_date, row.source_id);
}

const daily = readCsv("hormuz_daily.csv");
assert(
  JSON.stringify(daily.map((row) => row.date)) === JSON.stringify(dateRange(startDate, endDate)),
  "daily dates must be unique, contiguous, and cover 2026-01-01 through 2026-07-24",
);
for (const [index, row] of daily.entries()) {
  const context = "hormuz_daily.csv:" + (index + 2);
  assert(coverageStatuses.has(row.coverage_status), context + ": invalid coverage_status");
  assert(
    qualifiers.has(row.verified_crossings_all_qualifier),
    context + ": invalid crossing qualifier",
  );
  assert(qualifiers.has(row.oil_volume_qualifier), context + ": invalid volume qualifier");
  for (const field of dailyNumeric) parseNonnegative(row[field], context + " " + field);
  const usedSources = splitSources(row.source_ids);
  const unknown = usedSources.filter((sourceId) => !sourceIds.has(sourceId));
  assert(!unknown.length, context + ": unknown source IDs " + unknown.join(", "));
  const hasValue = [...dailyNumeric].some((field) => row[field] !== "");
  assert(!hasValue || usedSources.length, context + ": observed values require media source IDs");
  if (row.verified_crossings_all_alt) {
    assert(
      row.coverage_status === "conflict",
      context + ": alternate count requires conflict status",
    );
  }
  if (["no_daily_report_found", "provisional"].includes(row.coverage_status)) {
    assert(!hasValue, context + ": missing/provisional rows cannot contain values");
  }
}

const observations = readCsv("hormuz_observations.csv");
const observationIds = new Set(observations.map((row) => row.observation_id));
assert(observationIds.size === observations.length, "duplicate observation_id");
for (const [index, row] of observations.entries()) {
  const context = "hormuz_observations.csv:" + (index + 2);
  const start = parseIsoDate(row.observation_start, context);
  const end = parseIsoDate(row.observation_end, context);
  assert(start <= end, context + ": observation_start after observation_end");
  assert(row.value !== "", context + ": value is required");
  parseNonnegative(row.value, context + " value");
  assert(qualityFlags.has(row.quality_flag), context + ": invalid quality_flag");
  const usedSources = splitSources(row.source_ids);
  assert(usedSources.length, context + ": media source is required");
  const unknown = usedSources.filter((sourceId) => !sourceIds.has(sourceId));
  assert(!unknown.length, context + ": unknown source IDs " + unknown.join(", "));
  assert(row.data_provider, context + ": data_provider is required");
}

const cited = new Set(
  [...daily, ...observations].flatMap((row) => splitSources(row.source_ids)),
);
const uncited = [...sourceIds].filter((sourceId) => !cited.has(sourceId));
assert(!uncited.length, "source registry contains uncited rows: " + uncited.join(", "));

console.log(
  "Validated " + daily.length + " daily rows, " + observations.length +
    " observations, and " + sources.length + " media sources.",
);
