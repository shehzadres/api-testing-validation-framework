const { faker: base } = require("@faker-js/faker/locale/en");

const namespaceAliases = {
  address: "location",
  name: "person",
  random: "helpers"
};

const methodAliases = {
  "name.findName": "person.fullName",
  "random.word": "word.sample",
  "random.alphaNumeric": "string.alphanumeric",
  "datatype.number": "number.int",
  "datatype.uuid": "string.uuid",
  "phone.phoneNumberFormat": "phone.number",
  "company.companyName": "company.name",
  "company.companySuffix": "company.name",
  "company.bs": "company.buzzPhrase",
  "company.bsAdjective": "company.buzzAdjective",
  "company.bsBuzz": "company.buzzVerb",
  "company.bsNoun": "company.buzzNoun",
  "image.imageUrl": "image.url",
  "internet.userName": "internet.username",
  "internet.ip": "internet.ipv4",
  "internet.color": "color.rgb",
  "commerce.product": "commerce.productName"
};

function resolve(path) {
  const parts = path.split(".");
  let value = base;
  for (const part of parts) {
    if (value == null) return undefined;
    value = value[part];
  }
  return value;
}

const legacy = new Proxy({}, {
  get(_target, namespace) {
    const name = String(namespace);
    const actualNamespace = namespaceAliases[name] || name;
    const target = base[actualNamespace] || {};
    return new Proxy(target, {
      get(ns, method) {
        const key = name + "." + String(method);
        const path = methodAliases[key] || actualNamespace + "." + String(method);
        const value = resolve(path);
        if (typeof value === "function") {
          const owner = resolve(path.split(".").slice(0, -1).join("."));
          return value.bind(owner);
        }
        if (value !== undefined) return value;
        return () => base.word.sample();
      }
    });
  }
});

module.exports = legacy;
