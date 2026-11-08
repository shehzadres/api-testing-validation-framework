const dynamicVariables = require("postman-collection/lib/superstring/dynamic-variables");

for (const key of ["$randomCity", "$randomFirstName", "$randomEmail", "$randomUUID"]) {
  const variable = dynamicVariables[key];
  if (!variable || typeof variable.generator !== "function") {
    throw new Error(key + " has no working generator");
  }
  const value = variable.generator();
  if (typeof value !== "string" || value.length === 0) {
    throw new Error(key + " returned an empty or non-string value");
  }
  process.stdout.write(key + " -> " + value + "\n");
}
