const fs = require("node:fs");
const path = require("node:path");

const target = path.join(__dirname, "..", "node_modules", "postman-collection", "lib", "superstring", "dynamic-variables.js");
if (!fs.existsSync(target)) {
  throw new Error("Could not locate Newman Postman dynamic-variable helper: " + target);
}

const original = fs.readFileSync(target, "utf8");
const legacyImport = "var faker = require('@faker-js/faker/locale/en'),";
const compatibilityImport = "var faker = require('../../../../scripts/newman-faker-compat.cjs'),";

if (original.includes(compatibilityImport)) {
  console.log("Newman Faker compatibility patch already applied.");
} else if (original.includes(legacyImport)) {
  fs.writeFileSync(target, original.replace(legacyImport, compatibilityImport), "utf8");
  console.log("Applied Newman Faker compatibility patch.");
} else {
  throw new Error("Newman Faker import changed; review the upstream dependency before patching.");
}
